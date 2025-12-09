extends Control

var _next_data_to_pred: PackedByteArray
var _waiting_for_pred: bool = false
var _next_check_queued: bool = false

@onready var digits_container = %DigitsContainer
@onready var paint_area = %PaintArea
@onready var fine_tune_saver = $FineTuneDataSaver
@onready var api_conn = $ApiConnection

func _ready() -> void:
	var clear_btn: Button = %ClearButton
	clear_btn.pressed.connect(paint_area.clear_viewport)
	
	paint_area.redrawed.connect(_on_new_img_to_pred)
	
	digits_container.digit_clicked.connect(_on_digit_clicked)
	
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
	
	var proba = await api_conn.predict(_next_data_to_pred)
	
	if proba != null:
		for i in proba.size():
			proba[i] *= 255
		
		digits_container.apply_preds(proba)
	
	_waiting_for_pred = false
	
	if _next_check_queued:
		_check_model_pred()


func _input(event: InputEvent) -> void:
	if event is not InputEventKey:
		return
	
	if event is InputEventWithModifiers and event.is_pressed() and event.keycode == KEY_O and event.ctrl_pressed:
		$FileDialog.popup()


func _on_folder_selected(folder_path: String) -> void:
	Settings.model_folder_path = folder_path
	Settings.first_time_loaded = false
	Settings.save_settings()


func _image_to_str_array(image: Image) -> PackedStringArray:
	var data = PackedStringArray()
	data.resize(28*28)
	
	assert(image.get_format() == Image.Format.FORMAT_L8, "Image format should be right!")
	
	var image_data = image.get_data()
	
	for i in range(image_data.size()):
		data[i] = str(image_data[i])
	
	return data


func _on_digit_clicked(digit: int) -> void:
	var image = paint_area.get_image()
	var data = _image_to_str_array(image)
	fine_tune_saver.save_row(data, digit)
