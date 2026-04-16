import sys

if len(sys.argv) < 3:
    print("Add both arguments!")
    exit(1)

content = sys.argv[1]
input_file_name = sys.argv[2]

with open(input_file_name, "w") as output_file:
    output_file.write(content)
    output_file.flush()

print(f"Done! Pushed to {input_file_name}\n")
print(content)
