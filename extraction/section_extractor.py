def find_relevant_sections(sections):
    method_text = ""
    experiment_text = ""

    for sec in sections:
        lower = sec.lower()

        if "method" in lower or "approach" in lower:
            method_text += sec[:2000]

        if "experiment" in lower or "evaluation" in lower:
            experiment_text += sec[:2000]

    return method_text, experiment_text