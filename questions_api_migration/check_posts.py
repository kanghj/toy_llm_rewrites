import os

def split_xml_by_lines(file_path, output_dir, lines_per_file=100):
    os.makedirs(output_dir, exist_ok=True)

    with open(file_path, 'r') as infile:
        file_count = 1
        lines = []

        for line in infile:
            lines.append(line)
            if len(lines) >= lines_per_file:
                output_file_path = os.path.join(output_dir, f"split_{file_count}.xml")
                with open(output_file_path, 'w') as outfile:
                    outfile.writelines(lines)
                    outfile.writelines("</posts>")
                print(f"Written {output_file_path}")
                file_count += 1
                lines = []

        # Write any remaining lines to the last file
        if lines:
            output_file_path = os.path.join(output_dir, f"split_{file_count}.xml")
            with open(output_file_path, 'w') as outfile:
                outfile.writelines(lines)
            print(f"Written {output_file_path}")

# Example usage
file_path = 'Posts.xml'
output_dir = 'SO_chunk_by_line'
split_xml_by_lines(file_path, output_dir, lines_per_file=100000)
