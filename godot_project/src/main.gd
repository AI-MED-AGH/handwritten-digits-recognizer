extends Control

const MODEL_INPUT_FILE = "model_input.pipe"
const MODEL_OUTPUT_FILE = "model_output.pipe"
const ECHO_TO_INPUT_FILE = "echo_to_input.py"

var _next_data_to_pred: PackedByteArray
var _waiting_for_pred: bool = false
var _next_check_queued: bool = false

@onready var digits_container = %DigitsContainer


func _ready() -> void:
	var paint_area = %PaintArea
	var clear_btn: Button = %ClearButton
	clear_btn.pressed.connect(paint_area.clear_viewport)
	
	paint_area.redrawed.connect(_on_new_img_to_pred)
	
	$FileDialog.dir_selected.connect(_on_folder_selected)
	if Settings.first_time_loaded:
		$FileDialog.popup()


func _on_new_img_to_pred(image: Image) -> void:
	_next_check_queued = true
	_next_data_to_pred = image.get_data()
	_check_model_pred()


func _check_model_pred() -> void:
	if _waiting_for_pred:
		return
	
	_next_check_queued = false
	_waiting_for_pred = true
	
	var input_data = PackedStringArray()
	input_data.resize(28*28)
	
	var input_idx = 0
	for i in range(_next_data_to_pred.size()):
		input_data[input_idx] = str(_next_data_to_pred[i])
		input_idx += 1
	
	_push_model_input(input_data)
	
	await _await_model_prediction()
	
	_waiting_for_pred = false
	
	if _next_check_queued:
		_check_model_pred()


func _push_model_input(model_input: PackedStringArray) -> void:
	var model_input_str = ",".join(model_input)
	
	var echo_to_input_program = Settings.model_folder_path.path_join(ECHO_TO_INPUT_FILE)
	var input_file_path = Settings.model_folder_path.path_join(MODEL_INPUT_FILE)
	
	var output = []
	var result = OS.execute("python3", [echo_to_input_program, model_input_str, input_file_path], output)
	
	if result != 0:
		print("error pushing to file: ", result)
		print("output:\n", output)
	#print("output:\n", output)
	#print("\n\n\n===")


func _await_model_prediction():
	var output_path = Settings.model_folder_path.path_join(MODEL_OUTPUT_FILE)

	var output = OS.execute_with_pipe("cat", [output_path])
	print(output)
	
	if output.is_empty():
		print("Error creating subprocess")
		return PackedInt32Array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
		
	var stdout: FileAccess = output.stdio
	
	var text = stdout.get_as_text()
	
	const MAX_WAIT = 0.5
	const DELAY: float = 0.05
	var elapsed_time: float = 0.0
	
	while text == "":
		if elapsed_time >= MAX_WAIT:
			return
		
		await get_tree().create_timer(DELAY).timeout
		elapsed_time += DELAY
		text = stdout.get_as_text()
	
	print("TExt: '%s'" % text)
	
	var output_text = text.split(",")
	var predictions = PackedInt32Array()
	predictions.resize(10)
	
	for i in range(output_text.size()):
		predictions[i] = output_text[i].to_int()
	
	print("Preds: ", predictions)
	
	digits_container.apply_preds(predictions)


func _input(event: InputEvent) -> void:
	if event is not InputEventKey:
		return
	
	if event is InputEventWithModifiers and event.is_pressed() and event.keycode == KEY_O and event.ctrl_pressed:
		$FileDialog.popup()


func _on_folder_selected(folder_path: String) -> void:
	Settings.model_folder_path = folder_path
	Settings.first_time_loaded = false
	Settings.save_settings()
