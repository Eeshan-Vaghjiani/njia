"""Small practice checks with fixed answer keys, not a certification."""
from .engine import display

# prompt, options, correct index, explanation
BANK = {
    "sql": [
        ("Which JOIN keeps every row from the left table, even without a match?", ["INNER JOIN", "LEFT JOIN", "CROSS JOIN"], 1, "LEFT JOIN preserves left-side rows and returns NULL for missing right-side matches."),
        ("Which clause filters groups after aggregation?", ["WHERE", "ORDER BY", "HAVING"], 2, "HAVING filters aggregate groups; WHERE filters rows before grouping."),
        ("How do you count unique customer IDs?", ["COUNT(DISTINCT customer_id)", "SUM(customer_id)", "COUNT(*)"], 0, "COUNT(DISTINCT ...) counts distinct non-NULL values."),
    ],
    "r": [
        ("Which dplyr verb keeps rows matching a condition?", ["select()", "filter()", "rename()"], 1, "filter() selects rows; select() selects columns."),
        ("What does is.na(x) identify?", ["Missing values", "Duplicate rows", "Negative values"], 0, "is.na() returns a logical indicator of missing values."),
        ("In ggplot2, what does aes() describe?", ["File encoding", "Data-to-visual mappings", "Database credentials"], 1, "aes() maps variables to visual properties such as x, y, and colour."),
    ],
    "python": [
        ("Which Python collection stores key-value pairs?", ["list", "set", "dict"], 2, "A dict maps keys to values."),
        ("What is a safe first step when a CSV contains missing values?", ["Delete every incomplete row immediately", "Inspect missingness and its context", "Replace every missing value with zero"], 1, "Inspect the pattern and meaning of missingness before choosing a treatment."),
        ("Why use a virtual environment?", ["To isolate project dependencies", "To encrypt all data", "To guarantee faster execution"], 0, "Virtual environments isolate dependency versions between projects."),
    ],
    "excel": [
        ("Which feature summarizes sales by region without writing a formula for each region?", ["Spell check", "Pivot table", "Page layout"], 1, "Pivot tables group and aggregate data interactively."),
        ("What does $A$1 mean in a formula?", ["An absolute cell reference", "A currency value", "An invalid reference"], 0, "Both column and row stay fixed when the formula is copied."),
        ("Before combining monthly sheets, what should you check?", ["That all tabs have different colours", "That column names and types align", "That every number is formatted as text"], 1, "Consistent schemas avoid silently misaligned or unusable data."),
    ],
    "power bi": [
        ("Which language is used for measures in Power BI?", ["CSS", "DAX", "Bash"], 1, "DAX defines measures and calculated columns."),
        ("What does a one-to-many relationship usually connect?", ["A unique dimension key to repeated fact keys", "Two unrelated chart colours", "Two identical report pages"], 0, "Dimension tables typically have unique keys referenced by many fact rows."),
        ("What should you check if a total doubles after a join?", ["Font size", "Refresh animation", "Join keys and relationship cardinality"], 2, "Duplicate keys or incorrect cardinality can multiply rows and totals."),
    ],
    "docker": [
        ("What is a Docker image?", ["A running process only", "A packaged template for containers", "A virtual monitor"], 1, "An image is the template used to create a container."),
        ("Where should persistent application data usually live?", ["Only in the writable container layer", "In the Dockerfile", "In a volume or deliberate external store"], 2, "Volumes survive replacement of an individual container."),
        ("Why pin a base image version?", ["To improve reproducibility", "To eliminate every vulnerability", "To avoid using a Dockerfile"], 0, "Pinning makes builds more reproducible, though updates and security review remain necessary."),
    ],
}


def questions(skill):
    return {"skill": skill, "label": display(skill), "questions": [{"id": i, "prompt": q[0], "options": q[1]} for i, q in enumerate(BANK[skill])], "reflection": f"Describe a small project where you would use {display(skill)}. What would you check before trusting the result?", "method": "Three fixed, automatically marked practice questions. The reflection is self-review only. Not a certification or proof of job readiness."}


def grade(skill, answers):
    feedback = [{"question": q[0], "selected": q[1][answer], "correct": answer == q[2], "expected": q[1][q[2]], "explanation": q[3]} for q, answer in zip(BANK[skill], answers)]
    score = sum(f["correct"] for f in feedback)
    return {"skill": skill, "label": display(skill), "correct": score, "total": len(feedback), "feedback": feedback, "summary": "Strong start on these fundamentals. Apply them in a project next." if score == len(feedback) else "Use the explanations below, practice the concepts, and try again.", "method": "Fixed answer-key scoring; a short practice result, not independently verified proficiency."}
