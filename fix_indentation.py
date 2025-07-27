def fix_indentation():
    with open('src/main.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Find the main function
    main_start_line = -1
    for i, line in enumerate(lines):
        if line.strip() == 'def main():':
            main_start_line = i
            break

    if main_start_line == -1:
        print("Could not find main function")
        return

    # Fix indentation in the main function
    fixed_lines = []
    for i, line in enumerate(lines):
        if i == main_start_line:
            fixed_lines.append(line)
            # Add proper indentation to the next line if it's not indented
            if i + 1 < len(lines) and not lines[i + 1].startswith(' '):
                fixed_lines.append('    ' + lines[i + 1])
                i += 1  # Skip the next line since we've already processed it
            continue
        fixed_lines.append(line)

    # Write the fixed content back to the file
    with open('src/main.py', 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)

    print("Fixed indentation in main function")

if __name__ == "__main__":
    fix_indentation()