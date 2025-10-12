extends ColorRect


func _ready() -> void:
	$Label.text = str(get_index())
