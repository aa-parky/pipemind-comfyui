pipemind_select_line – Custom ComfyUI Node

Overview

pipemind_select_line.py is a self-contained ComfyUI node that reads a text file from your ComfyUI input directory and outputs one specific line according to a variety of selection strategies.

Key features:
	•	Six line-selection modes (manual, random, increment, decrement, custom sequence, custom random).
	•	Always-on Ignore indices field to omit any line numbers or ranges from selection.
	•	Deterministic random behaviour via a user-supplied seed.
	•	Batch-persistent state so increment/decrement and custom sequences continue where they left off across batches.
	•	Built-in preview with zero-based line numbers for easy reference.

⸻

Prerequisites
	•	A working ComfyUI installation (tested with ComfyUI >= 0.3.5).
	•	Python 3.10+.

This node is 100 % pure-Python and has no external dependencies beyond the Python standard library.

⸻

Installation
	1.	Copy the file pipemind_select_line.py into any folder scanned by ComfyUI for custom nodes (e.g. custom_nodes/pipemind).
	2.	Restart ComfyUI. The node appears under Pipemind / Custom → SelectLineFromDropdown.

Tip  If you’re packaging multiple Pipemind nodes, keep them in a dedicated folder so the JavaScript bundle can sit alongside the Python file.

⸻

Node UI Reference

Field	Type	Purpose
enabled	Boolean	Soft on/off switch (skips execution when False).
file_name	Dropdown	Lists every .txt file anywhere inside the ComfyUI input/ directory. Paths are shown relative to input/.
mode	Enum	Selection algorithm (see Modes below).
line_index	Int	0-based index used by manual, increment and decrement modes as the starting position.
seed	Int	PRNG seed for random and custom_random modes. Identical seed → identical result.
custom_indices	String	Comma-separated list of individual indices and/or ranges (1,4,10-12). Used by custom_seq and custom_random.
ignore_indices	String	New in 2025-06-22. Same syntax as above; any matching lines are excluded from all modes. Leave empty to disable.


⸻

Basic Usage
	1.	Place one or more text files in ComfyUI/input/ (or sub-folders).
	2.	Add SelectLineFromDropdown to your workflow.
	3.	Choose the file and desired mode.
	4.	(Optional) Enter indices to ignore – for example 0, 3-5 skips the first line and lines 3 to 5.
	5.	The node outputs:
	1.	selected_line – the chosen line (string)
	2.	line_count – total number of non-blank lines
	3.	current_index – 0-based index of the selected line
	4.	file_preview – entire file with numbered lines (for UI display / debugging)

Connect selected_line to any downstream prompt-building nodes.

⸻

Modes in Detail

Mode	Behaviour
manual	Returns line_index (unless ignored).
random	Picks a random available line using seed.
increment	First run → closest available ≥ line_index; subsequent runs in the same batch → next higher available, wrapping at EOF.
decrement	Same as increment but counts downward.
custom_seq	Cycles through custom_indices in the given order (ignoring any out-of-range or ignored lines). Remembers position across the batch.
custom_random	Uniformly random choice from the valid custom_indices, seeded.

If all lines end up ignored, the node returns [Error: All lines are ignored] and halts gracefully.

⸻

Output Preview Example

 0:  Prompt: A cosy cabin at dawn
 1:  Prompt: A cyberpunk alley at night
 2:  Prompt: A tropical beach at sunset
 3:  Prompt: An underwater reef scene

The preview is handy for picking indices to use in other fields.

⸻

Error Messages

Message	Reason / Fix
[Error: File not found]	Selected file was removed/renamed. Choose another file or refresh the list by restarting ComfyUI.
[Error: File is empty]	The chosen file contains only blank lines. Add content.
[Error: All lines are ignored]	Your ignore_indices excludes every line. Adjust the list.
[Error: Selected line is ignored]	manual mode picked a line listed in ignore_indices. Use another index.

Other unexpected exceptions are caught and reported as [Error: ...] with the original message.

⸻

Code Walk-through

The implementation fits in a single file (~240 LOC). Major parts:
	1.	Constants & Helpers
	•	COMFY_INPUT_DIR – absolute path to the ComfyUI input folder.
	•	list_txt_files_recursive() – builds the dropdown list.
	•	parse_custom_indices() – converts strings like 1,4,7-9 into [1,4,7,8,9].
	•	add_line_numbers() – pretty-prints the file with aligned zero-based indices.
	2.	SelectLineFromDropdown class
	•	INPUT_TYPES() defines the UI; note the new ignore_indices field.
	•	_batch_state stores small per-batch tuples so increment and custom_seq keep position.
	•	_apply_ignore() and _next_valid() encapsulate ignore-list logic and wrap-around navigation.
	3.	run() method
	1.	Reads & sanitises the file (blank lines stripped, trailing \n removed).
	2.	Builds ignore_set and filters out those indices to form available.
	3.	Switches on mode to select idx using helper functions and RNG (random.Random(seed)).
	4.	Returns the required four outputs.
	4.	JavaScript
	•	Optional UI enhancements live in web/js/pipemind_selectLine.js (not required for core logic).

Adding New Modes

Implement additional strategies by extending the elif chain in run() and updating the mode list in INPUT_TYPES().

⸻

Version History
	•	2025-06-22  Add Ignore indices field; documentation overhaul.
	•	2025-03-10  Initial public release with six selection modes.

⸻

License

Released under the MIT License (see project root for full text).

⸻

Contact & Support

Questions, feature requests, or bug reports? Ping Parky in the ComfyUI Discord or open an issue in the Pipemind repository.