# This module generates a multi-page PDF report for UO grade distributions in a certain major.
# The report is generated w/ PdfPages in matplotlib and served in-memory for web download.

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from datetime import datetime

import matplotlib

# Use a headless environment b/c the code will run on the server w/ no display
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.figure import Figure

from models import GradeCounts, InstructorDistribution, TermCourseData, get_degree_title, get_term_course_data

# Fixed x-axis bar order for each chart
GRADE_LABELS = ("A", "B", "C", "DNF")
# Bar colors for A/B/C/DNF respectively
BAR_COLORS = ("#21E051", "#CDF518", "#E7A820", "#565656")

# These layout values are normalized figure coords (from 0.0 to 1.0)
# This keeps visual sizing consistent regardless across pages
PAGE_LEFT_MARGIN = 0.08
PAGE_RIGHT_MARGIN = 0.06
PAGE_TOP_MARGIN = 0.05
PAGE_BOTTOM_MARGIN = 0.08

# Spacing constants used by the page layout engine
# Controls the spacing between term headers, course titles, graph rows, etc.
HEADER_BLOCK_HEIGHT = 0.055
COURSE_TITLE_HEIGHT = 0.025
COURSE_TO_GRAPH_GAP = 0.006
GRAPH_ROW_HEIGHT = 0.16
GRAPH_ROW_GAP = 0.05
COURSE_SECTION_GAP = 0.06
GRAPH_COL_GAP = 0.05

# Width for each graph panel when placing 3 graphs side-by-side.
# Computed from total width minus edge/column margins.
GRAPH_WIDTH = (1.0 - PAGE_LEFT_MARGIN - PAGE_RIGHT_MARGIN - (2 * GRAPH_COL_GAP)) / 3.0


def _to_percentages(grade_counts: GradeCounts) -> tuple[float, float, float, float]:
	"""Convert student counts into percentages in A/B/C/DNF order"""
	# Ensure we have 4 categories
	if len(grade_counts) != 4:
		raise ValueError("grade_counts must be a 4-tuple in the form (A, B, C, DNF).")

	total_students = sum(grade_counts)
	# Avoid dividing by zero if there's no data
	if total_students <= 0:
		return (0.0, 0.0, 0.0, 0.0)

	# Finally, convert counts to percentages
	return tuple((count / total_students) * 100 for count in grade_counts)


def create_grade_bar(
	instructor_name: str,
	grade_counts: GradeCounts,
	ax: Axes | None = None,
) -> Axes:
	"""
	Creates a single grade distribution bar graph.

	Args:
		instructor_name: Professor name used for the x-axis label
		grade_counts: 4-tuple of grade counts in this order: (A, B, C, DNF)
		ax: Pre-existing matplotlib axis (if omitted, it'll be created)
	"""
	# Convert grade counts to percentages
	percentages = _to_percentages(grade_counts)

	# Allow this function to be used on its own if axes aren't already created
	if ax is None:
		_, ax = plt.subplots(figsize=(4, 3))

	# Draw one bar per grade category
	bars = ax.bar(
		GRADE_LABELS,
		percentages,
		color=BAR_COLORS,
		edgecolor="#2F2F2F",
		linewidth=0.8,
	)

	# Keep all charts on the exact same y-level
	ax.set_ylim(0, 100)
	ax.set_yticks([0, 20, 40, 60, 80, 100])
	# ax.set_ylabel("Grade Distribution")
	ax.set_xlabel(instructor_name)
	# Horizontal gridlines
	ax.grid(axis="y", linestyle="--", alpha=0.35)

	# Add percentage values above the bars
	for bar, percentage in zip(bars, percentages):
		ax.text(
			bar.get_x() + (bar.get_width() / 2),
			min(100, bar.get_height()) + 1.2,
			f"{percentage:.1f}%",
			ha="center",
			va="bottom",
			fontsize=8,
		)

	return ax


def _format_instructor_graphs(instructor_graphs: list[InstructorDistribution]) -> list[list[InstructorDistribution]]:
	"""Split instructor list into rows of size 3 or less.
	Also, add an 'All Instructors' graph at the beginning by summing counts across all instrcutors."""
	if len(instructor_graphs) > 1:
		total_grade_counts = [sum(counts[i] for _, counts in instructor_graphs) for i in range(4)]
		instructor_graphs.insert(0, ("ALL INSTRUCTORS", tuple(total_grade_counts)))
	return [instructor_graphs[idx : idx + 3] for idx in range(0, len(instructor_graphs), 3)]


def _build_term_pages(major_name: str, term_name: str, courses: dict[str, list[InstructorDistribution]]) -> list[Figure]:
	"""Build the page(s) for a term w/ fixed-size charts/spacing"""
	# Build pages manually w/ absolute coords so layout is consistent
	pages: list[Figure] = []
	page_index = -1
	figure: Figure | None = None
	cur_y = 0.0 # keeps track of the next free y-position on page

	def start_page() -> None:
		nonlocal page_index, figure, cur_y
		# Each new page resets vertical cursor and repeats the heading block.
		page_index += 1
		if figure is not None:
			plt.close(figure) # close previous page-figure to free memory
		figure = plt.figure(figsize=(11, 14))
		pages.append(figure)

		header_top = 1.0 - PAGE_TOP_MARGIN
		# If continuing a term page, append "(continued)" to the name
		term_heading = term_name if page_index == 0 else f"{term_name} (continued)"
		# figure.text places text directly in figure coords from 0-1 where (0, 1) is top-left of page
		figure.text(PAGE_LEFT_MARGIN, header_top, f"Major: {major_name}", fontsize=16, weight="bold", va="top")
		figure.text(PAGE_LEFT_MARGIN, header_top - 0.03, term_heading, fontsize=16, weight="bold", va="top")
		cur_y = header_top - HEADER_BLOCK_HEIGHT

	def section_height(graph_rows_count: int) -> float:
		# Estimate course block height to decide whether the content fits on one page
		if graph_rows_count <= 0:
			return COURSE_TITLE_HEIGHT + COURSE_SECTION_GAP
		return (
			COURSE_TITLE_HEIGHT
			+ COURSE_TO_GRAPH_GAP
			+ (graph_rows_count * GRAPH_ROW_HEIGHT)
			+ (max(0, graph_rows_count - 1) * GRAPH_ROW_GAP)
			+ COURSE_SECTION_GAP
		)

	start_page() # every term starts on a fresh page

	for course_name, instructor_graphs in courses.items():
		# Format list of instructor data into rows of 3 & add 'All Instructors' graph
		graph_rows = _format_instructor_graphs(instructor_graphs)
		height_needed = section_height(len(graph_rows))

		# If course doesn't fit, spill onto next page
		if cur_y - height_needed < PAGE_BOTTOM_MARGIN:
			start_page()

		# Avoid NPEs just in case
		if figure is None:
			continue

		# Print course title
		figure.text(
			PAGE_LEFT_MARGIN,
			cur_y - (COURSE_TITLE_HEIGHT / 2),
			course_name,
			fontsize=12,
			weight="bold",
			va="center",
		)
		cur_y -= COURSE_TITLE_HEIGHT

		# Add gap b/t course title & graphs
		if graph_rows:
			cur_y -= COURSE_TO_GRAPH_GAP

		# For each row of graphs
		for row_idx, row_graphs in enumerate(graph_rows):
			# Check if we need to start new page before drawing each row
			if cur_y - GRAPH_ROW_HEIGHT < PAGE_BOTTOM_MARGIN:
				start_page()
				if figure is None:
					continue
				# If we spilled to a new page, append "(continued)" for clarity
				figure.text(
					PAGE_LEFT_MARGIN,
					cur_y - (COURSE_TITLE_HEIGHT / 2),
					f"{course_name} (continued)",
					fontsize=12,
					weight="bold",
					va="center",
				)
				cur_y -= COURSE_TITLE_HEIGHT + COURSE_TO_GRAPH_GAP

			row_bottom = cur_y - GRAPH_ROW_HEIGHT # Get y-position of bottom of graph row
			for col in range(3):
				# Compute x-position of left edge of each graph in the row
				left = PAGE_LEFT_MARGIN + (col * (GRAPH_WIDTH + GRAPH_COL_GAP))
				# add_axes argument is [left, bottom, width, height] in figure coords (0 to 1)
				ax = figure.add_axes([left, row_bottom, GRAPH_WIDTH, GRAPH_ROW_HEIGHT])

				if col < len(row_graphs):
					instructor_name, grade_counts = row_graphs[col]
					# Draw the graph!
					create_grade_bar(instructor_name, grade_counts, ax=ax)
				else:
					# Hide leftover slots if # of graphs isn't a multiple of 3
					ax.axis("off")

			cur_y = row_bottom # move cursor to bottom of graph row
			if row_idx < len(graph_rows) - 1:
				# If not final row, add gap b/t graph rows
				cur_y -= GRAPH_ROW_GAP

		# Add gap before starting next course section
		cur_y -= COURSE_SECTION_GAP

	return pages


def _write_pdf(pdf: PdfPages, degree_id, year_from, year_to) -> None:
	"""Write the report pages to PdfPages"""

	# Query SQLite database for degree name & course/grade data
	major_name = get_degree_title(degree_id) or "Unknown Degree"
	course_data = get_term_course_data(degree_id, year_from, year_to)

	# Text for the front page of the report
	front_page_text1 = f"""The following report charts the grades assigned
across all required UO courses for this major.
Data is from {year_from}-{year_to}."""
	front_page_text2 = f"""Report generated on {datetime.now().strftime("%B %d, %Y")} by the MaxGPA system created for
Hornof's Spring 2026 CS 422 Software Methodology by the following students:

Harrison Ramos
Ryder Gilman
Reed Nystrom
Ben Elster
Nate Wong"""
	
	total_grade_counts = GradeCounts((0, 0, 0, 0))
	for term_courses in course_data.values():
		for instructor_graphs in term_courses.values():
			for _, grade_counts in instructor_graphs:
				total_grade_counts = GradeCounts((
					total_grade_counts[0] + grade_counts[0],
					total_grade_counts[1] + grade_counts[1],
					total_grade_counts[2] + grade_counts[2],
					total_grade_counts[3] + grade_counts[3],
				))
	
	gpa_prediction = (4.0 * total_grade_counts[0] + 3.0 * total_grade_counts[1] + 2.0 * total_grade_counts[2]) / (
		total_grade_counts[0] + total_grade_counts[1] + total_grade_counts[2]
	)
	front_page_graph_text = f"""Overall grade distribution across all required courses in this degree plan.
GPA Prediction: {gpa_prediction:.2f}"""

	front_page_fig = plt.figure(figsize=(11, 14))
	header_top = 1.0 - PAGE_TOP_MARGIN * 2 # add extra margin on first page
	front_page_fig.text(0.5, header_top, f"Degree: {major_name}", fontsize=16, weight="bold", ha="center", va="top")
	front_page_fig.text(0.5, header_top - 0.03, front_page_text1, fontsize=16, ha="center", va="top")
	front_page_fig.text(0.5, header_top - 0.13, front_page_text2, fontsize=10, ha="center", va="top")
	# Add overall grade distribution for the entire major on the front page
	create_grade_bar("ALL COURSES", total_grade_counts, ax=front_page_fig.add_axes([0.35, PAGE_TOP_MARGIN * 2, 0.3, 0.2]))
	# Add explanatory text above the ALL COURSES graph
	front_page_fig.text(0.5, PAGE_TOP_MARGIN * 2 + 0.2 + 0.02, front_page_graph_text, fontsize=12, weight="bold", ha="center", va="bottom")
	pdf.savefig(front_page_fig)
	plt.close(front_page_fig)

	# Each term starts on new page, and if it doesn't fit on 1 page, it'll overflow to new ones
	for term_name, courses in course_data.items():
		for page in _build_term_pages(major_name, term_name, courses):
			# Save & close figures to free up memory
			pdf.savefig(page)
			plt.close(page)


def generate_pdf_bytes(degree_id, year_from, year_to) -> bytes:
	"""Generate the report in memory and return PDF bytes for web download"""
	pdf_buffer = BytesIO()

	with PdfPages(pdf_buffer) as pdf:
		_write_pdf(pdf, degree_id, year_from, year_to)

	# Rewind to beginning so we stream the full PDF content
	pdf_buffer.seek(0)
	return pdf_buffer.getvalue()


# if __name__ == "__main__":
	# default_output = Path(__file__).resolve().parent / "degree_report.pdf"
	# generated_path = generate_pdf(default_output)
	# print(f"PDF generated at: {generated_path}")
