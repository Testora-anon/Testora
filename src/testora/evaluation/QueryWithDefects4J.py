from testora.prompts.Prompt1 import Prompt1
from testora.util.Defects4J import get_target_bugs

# Choose how to extract code to be used in prompt:
from testora.prompts.CodeExtractor import get_hunk_windows_and_patch as get_code_and_patch
# from buggpt.prompts.CodeExtractor import get_full_file_and_patch as get_code_and_patch

# Choose which language model to use:
# import buggpt.llms.MockModel as llm
# import buggpt.llms.RandomModel as llm
from testora.llms.LLMCache import LLMCache
import testora.llms.OpenAIGPT as uncached_llm
llm = LLMCache(uncached_llm)


def answer_matches_patch(warning, patch):
    # crude heuristic: count as matching if warning is <=k lines away from patch
    k = 1
    found_match = False
    for modified_file in patch.modified_files:
        for hunk in modified_file:
            patch_lines = [l.value.strip() for l in hunk]
            edited_line_indices = []
            for idx, l in enumerate(hunk):
                if not l.is_context:
                    edited_line_indices.append(idx)
            for warning_line in warning["code"]:
                warning_line = warning_line.strip()
                if warning_line in patch_lines:
                    warning_line_idx = patch_lines.index(warning_line)
                    for edited_line_idx in edited_line_indices:
                        if abs(warning_line_idx - edited_line_idx) <= k:
                            found_match = True
                            break
    return found_match


target_bugs = get_target_bugs(
    "./data/defects4j_bugs_shuffled_March_7_2024_subset10.csv")

unparsable_answers = 0
true_positives = 0
false_positives = 0
true_negatives = 0
false_negatives = 0

for project_id, bug_id in target_bugs:
    for version in ["b", "f"]:
        print(f"\n{'Fixed' if version == 'f' else 'Buggy'} version of {project_id} {bug_id}\n-----------------------------------------")
        code, patch = get_code_and_patch(
            project_id, bug_id, version=version)
        p = Prompt1(code)
        raw_answer = llm.query(p)
        answer = p.parse_answer(raw_answer)
        print(f"Answer: {answer}\n")
        if answer is None:
            unparsable_answers += 1
        elif version == "f":
            if len(answer["warnings"]) > 0:
                false_positives += 1
                print(f"=> False positive")
            else:
                false_negatives += 1
                print(f"=> True negative")
        elif version == "b":
            has_match = False
            for warning in answer["warnings"]:
                if answer_matches_patch(warning, patch):
                    has_match = True
            if has_match:
                true_positives += 1
                print(f"=> True positive")
            else:
                false_negatives += 1
                print(f"=> False negative")
    print(f"============================================\n")

print(f"Summary:")
print(f"Unparsable answers: {unparsable_answers}")
print(f"True positives: {true_positives}")
print(f"False positives: {false_positives}")
print(f"True negatives: {true_negatives}")
print(f"False negatives: {false_negatives}")
precision = true_positives / (true_positives + false_positives)
print(f"Precision: {precision:.2f}")
recall = true_positives / (true_positives + false_negatives)
print(f"Recall: {recall:.2f}")
f1_score = (2 * precision * recall) / (precision +
                                       recall) if precision + recall > 0 else 0
print(f"F1 score: {f1_score:.2f}")
