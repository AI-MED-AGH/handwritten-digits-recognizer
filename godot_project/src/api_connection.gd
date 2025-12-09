extends Node

const API_URL = "http://0.0.0.0:8000"

var req = HTTPRequest.new()

func _ready() -> void:
	add_child(req)


func predict(img_data: PackedByteArray):
	var data_dict = {
		"data": [Array(img_data)],
	}
	var data_str = JSON.stringify(data_dict)
	var headers = PackedStringArray([
		'Content-Type: application/json',
	])
	var url = API_URL.path_join("predict")
	var err = req.request(url, headers, HTTPClient.METHOD_POST, data_str)
	
	if err != OK:
		printerr("Failed to send request: ", err)
		return null
	
	var resp_packed = await req.request_completed
	var result = resp_packed[0]
	var resp_code = resp_packed[1]
	var _resp_headers = resp_packed[2]
	var resp_body: String = resp_packed[3].get_string_from_ascii()
	var resp_dict = JSON.parse_string(resp_body)
	
	if result != req.RESULT_SUCCESS or resp_code != 200:
		printerr("Got error response:\n", resp_dict)
		return null
	
	var predicted_data: Dictionary = resp_dict["prediction"][0]
	#var pred_class = predicted_data["label"]
	var proba = predicted_data["proba"]
	return proba
