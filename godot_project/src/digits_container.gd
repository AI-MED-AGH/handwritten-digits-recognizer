extends HBoxContainer

@export var chosen_color: Color


func apply_preds(preds: PackedInt32Array) -> void:
	var best_score = preds[0]
	var best_idx = 0
	for i in range(1, preds.size()):
		if preds[i] > best_score:
			best_score = preds[i]
			best_idx = i
	
	for i in range(get_child_count()):
		var c = get_child(i)
		var pred = preds[i] / 255.0
		c.color = Color(pred, pred, pred, 255)

	if best_score > 0:
		get_child(best_idx).color = chosen_color
