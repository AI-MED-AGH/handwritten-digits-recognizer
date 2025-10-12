extends Node2D

var file_path = "/home/dom/Programming/python/handwritten_digits/model_output.pipe"
#var file_path = "/home/dom/Programming/python/handwritten_digits/test.txt"

func _ready() -> void:
	var output = OS.execute_with_pipe("cat", [file_path])
	print(output)
	
	if output.is_empty():
		print("Error creating subprocess")
		return
		
	var stdout: FileAccess = output.stdio
	
	var text = stdout.get_as_text()
	
	while text == "":
		await get_tree().create_timer(0.05).timeout
		text = stdout.get_as_text()
	
	print("TExt: '%s'" % text)
	print("ENDD")
