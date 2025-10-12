import sys

INPUT_PIPE_NAME = "/home/dom/Programming/python/handwritten_digits/model_input.pipe"

if len(sys.argv) < 2:
    print("Add the argument!")
    exit(1)

content = sys.argv[1]

with open(INPUT_PIPE_NAME, "w") as output_file:
    output_file.write(content)
    output_file.flush()

print(f"Done! Pushed to {INPUT_PIPE_NAME}\n")
print(content)
