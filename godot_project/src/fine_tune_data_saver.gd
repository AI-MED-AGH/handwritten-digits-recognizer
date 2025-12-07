extends Node

const FINE_TUNE_SHEET_FILENAME = "fine_tune_data.csv"
var _file: FileAccess

var _fine_tune_sheet_path: String


func _ready() -> void:
	_fine_tune_sheet_path = Settings.model_folder_path.path_join(FINE_TUNE_SHEET_FILENAME)
	_file = FileAccess.open(_fine_tune_sheet_path, FileAccess.WRITE)
	if _file == null:
		print("Error, cant open fine tune sheet: ", FileAccess.get_open_error())
		return


func save_row(data: PackedStringArray, ground_truth: int) -> void:
	print("Abut to save")
	if _file == null:
		return
	
	data.insert(0, str(ground_truth))
	_file.store_csv_line(data)
	_file.flush()
	
	print("saved to ", _fine_tune_sheet_path)
