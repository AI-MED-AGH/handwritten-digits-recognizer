extends Node

const _SETTINGS_FILEPATH = "user://settings.json"

@export_group("Settings")
var first_time_loaded: bool = true
var model_folder_path: String


func _init() -> void:
	_load_settings()


func _load_settings() -> void:
	var file = FileAccess.open(_SETTINGS_FILEPATH, FileAccess.READ)
	
	if file == null:
		return
	
	var json_text = file.get_as_text()
	var json = JSON.parse_string(json_text)
	
	for key in json.keys():
		set(key, json[key])


func save_settings() -> void:
	var json = {}
	json.first_time_loaded = first_time_loaded
	json.model_folder_path = model_folder_path
	
	var json_text = JSON.stringify(json)
	
	var file = FileAccess.open(_SETTINGS_FILEPATH, FileAccess.WRITE)
	
	if file == null:
		print("Error when saving settings: ", FileAccess.get_open_error())
		return
	
	file.store_string(json_text)
