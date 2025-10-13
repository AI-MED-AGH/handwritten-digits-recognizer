extends Control

var output_path = "/home/dom/Programming/python/handwritten_digits/model_output.pipe"
var echo_to_input_program = "/home/dom/Programming/python/handwritten_digits/echo_to_input.py"

var _waiting_for_pred: bool = false

@onready var digits_container = %DigitsContainer


func _ready() -> void:
	var paint_area = %PaintArea
	var clear_btn: Button = %ClearButton
	clear_btn.pressed.connect(paint_area.clear_viewport)
	
	paint_area.redrawed.connect(_check_model_pred)


func _check_model_pred(image: Image) -> void:
	if _waiting_for_pred:
		return
	
	_waiting_for_pred = true
	
	var data = image.get_data()
	#print(image.get_size())
	#print(data.size())
	#print(image.get_pixel(0, 0))
	
	var input_data = PackedStringArray()
	input_data.resize(image.get_size().x*image.get_size().y)
	
	var input_idx = 0
	for i in range(0, data.size(), 4):
		input_data[input_idx] = str(data[i])
		input_idx += 1
	
	_push_model_input(input_data)
	
	var preds = await _await_model_prediction()
	print("PRedsssS: ", preds)
	
	digits_container.apply_preds(preds)
	
	_waiting_for_pred = false


func _push_model_input(model_input: PackedStringArray) -> void:
	var model_input_str = ",".join(model_input)
	
	var output = []
	OS.execute("python3", [echo_to_input_program, model_input_str], output)
	
	print("output:\n", output)
	print("\n\n\n===")


func _await_model_prediction() -> PackedInt32Array:
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
	
	while text == "" and elapsed_time < MAX_WAIT:
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
	return predictions
