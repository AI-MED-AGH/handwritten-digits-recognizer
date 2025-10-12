extends HBoxContainer


func apply_preds(preds: PackedInt32Array) -> void:
	for i in range(get_child_count()):
		var c = get_child(i)
		var pred = preds[i] / 255.0
		c.color = Color(pred, pred, pred, 255)
