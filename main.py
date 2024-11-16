import tkinter as tk
from tkinter import filedialog, messagebox
import os
import re
import subprocess
from ttkbootstrap import Style
from tkinter.font import families
from tkinter import simpledialog
from PIL import Image, ImageTk
from tkinter import Menu
import autopep8
from tkinter import ttk
import webbrowser

current_file_path = None
file_content_changed = False  # Flag to track if file content has changed

# Dictionary to map file extensions to icon paths
ICON_PATHS = {
    '.txt': "Assets/code.png",
    '.py': "Assets/python.png",
    '.c': "Assets/c.png",
    '.cpp': "Assets/cplus.png",
    '.jpg': "Assets/jpg.png",
    '.png': "Assets/png.png",
    '.js': "Assets/js.png",
    '.xlsx': "Assets/xlsx.png",
    '.pdf': "Assets/pdf.png",
}

# FUNCTIONS

# Function to show message
def show_message(message):
    messagebox.showinfo("Message", message)

# Function to open a folder
def open_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        os.chdir(folder_path)
        populate_file_list(file_list, path=".")  # Pass the file_list argument here


# Function to open a file
def open_file():
    global file_content_changed, current_file_path
    file_path = filedialog.askopenfilename()
    if file_path:
        with open(file_path, 'r') as file:
            code_editor.delete(1.0, tk.END)
            code_editor.insert(tk.END, file.read())
        update_line_numbers()
        current_file_path = file_path
        file_content_changed = False  # Reset file content changed flag when opening a file
        apply_syntax_highlighting()  # Apply syntax highlighting after opening file

# Function to create a new file
def new_file():
    global file_content_changed, current_file_path
    file_path = filedialog.asksaveasfilename(defaultextension=".txt")
    if file_path:
        # Create an empty file at the specified path
        with open(file_path, 'w') as file:
            file.write('')
        # Refresh the file list to display the newly created file
        populate_file_list(file_list, path=".")  # Pass the file_list argument here
        current_file_path = file_path
        file_content_changed = False  # Reset file content changed flag when creating a new file

# Function to save the file
def save_file():
    global current_file_path, file_content_changed
    if current_file_path:  # If a file was already created
        with open(current_file_path, 'w') as file:
            file.write(code_editor.get(1.0, tk.END))
        file_content_changed = False  # Reset file content changed flag after saving
    else:  # If a file was not yet created
        new_file()

# Autosave function
def autosave():
    if autosave_enabled.get() and current_file_path:
        save_file()
    root.after(300, autosave)  # Autosave every 300 milliseconds

# Function to run the code
def run_code():
    global file_content_changed
    if file_content_changed and not autosave_enabled.get():
        show_message('Please save your code before running.')
    else:
        code = code_editor.get(1.0, tk.END)
        if current_file_path:
            file_name, file_extension = os.path.splitext(current_file_path)
            if file_extension == '.py':
                # Execute Python code
                execute_python_code(code)
            elif file_extension == '.cpp':
                # Execute C++ code
                execute_cpp_code(code)
            elif file_extension == '.c':
                # Execute C code
                execute_c_code(code)
            elif file_extension == '.js':
                # Execute JavaScript code
                execute_js_code(code)
            else:
                show_message('Unsupported file type for execution.')
        else:
            show_message('No file selected for execution.')

def execute_python_code(code):
    with open('temp.py', 'w') as file:
        file.write(code)
    try:
        output = subprocess.check_output(['python', 'temp.py'], stderr=subprocess.STDOUT, universal_newlines=True)
        display_output(output)
    except subprocess.CalledProcessError as e:
        display_output(e.output)

def execute_cpp_code(code):
    with open('temp.cpp', 'w') as file:
        file.write(code)
    try:
        subprocess.check_output(['g++', 'temp.cpp', '-o', 'temp'], stderr=subprocess.STDOUT, universal_newlines=True)
        output = subprocess.check_output(['./temp'], stderr=subprocess.STDOUT, universal_newlines=True)
        display_output(output)
    except subprocess.CalledProcessError as e:
        display_output(e.output)

def execute_c_code(code):
    with open('temp.c', 'w') as file:
        file.write(code)
    try:
        subprocess.check_output(['gcc', 'temp.c', '-o', 'temp'], stderr=subprocess.STDOUT, universal_newlines=True)
        output = subprocess.check_output(['./temp'], stderr=subprocess.STDOUT, universal_newlines=True)
        display_output(output)
    except subprocess.CalledProcessError as e:
        display_output(e.output)

def execute_js_code(code):
    with open('temp.js', 'w') as file:
        file.write(code)
    try:
        output = subprocess.check_output(['node', 'temp.js'], stderr=subprocess.STDOUT, universal_newlines=True)
        display_output(output)
    except subprocess.CalledProcessError as e:
        display_output(e.output)

# Function to display output on terminal
def display_output(output):
    terminal.config(state=tk.NORMAL)
    terminal.delete(1.0, tk.END)
    terminal.insert(tk.END, output)
    terminal.config(state=tk.DISABLED)

# Function to update line numbers
def update_line_numbers(event=None):
    global file_content_changed
    lines = code_editor.get(1.0, "end-1c").split("\n")  # Exclude the last character, which is always a newline
    line_numbers.config(state="normal")
    line_numbers.delete(1.0, "end")
    for i, line in enumerate(lines, start=1):
        line_numbers.insert("end", str(i) + "\n")
    line_numbers.config(state="disabled")
    file_content_changed = True  # Set file content changed flag when updating line numbers

# Function to populate file list
def populate_file_list(file_list, parent="", path="."):
    # Clear existing items in the file list
    file_list.delete(*file_list.get_children())

    # Dictionary to store mapping between directory paths and item IDs in the Treeview
    path_to_item_id = {}

    # Dictionary to store mapping between file names and icon images
    icon_images = {}

    # Function to recursively populate the file list
    def recursive_populate(parent_path="", parent_item=""):
        nonlocal path_to_item_id
        nonlocal icon_images
        entries = os.listdir(parent_path)
        for entry in sorted(entries):
            full_path = os.path.join(parent_path, entry)
            if os.path.isdir(full_path):
                # If the entry is a directory, add it to the Treeview and recursively populate its contents
                folder_name = os.path.basename(full_path)
                if not parent_item:
                    item_id = file_list.insert("", "end", text=folder_name, open=False)
                else:
                    item_id = file_list.insert(parent_item, "end", text=folder_name, open=False)
                # Store the mapping between directory path and item ID
                path_to_item_id[full_path] = item_id
                recursive_populate(full_path, item_id)
            else:
                # If the entry is a file, add it to the Treeview under its parent directory
                file_name = os.path.basename(entry)
                file_extension = os.path.splitext(entry)[1]
                icon_path = get_icon_path(entry)
                icon = icon_images.get(icon_path)
                if not icon:
                    # If the icon image is not already loaded, resize it and store it in the dictionary
                    img = Image.open(icon_path)
                    img = img.resize((15, 15))
                    icon = ImageTk.PhotoImage(img)
                    icon_images[icon_path] = icon
                file_list.insert(parent_item, "end", text=file_name, image=icon)

    # Populate the file list recursively starting from the specified path
    recursive_populate(path)

# Function to get the icon path based on file extension
def get_icon_path(file_name):
    _, ext = os.path.splitext(file_name)
    # Define paths to icons based on file extensions
    icon_paths = {
        '.txt': "Assets/code.png",
        '.py': "Assets/python.png",
        '.c': "Assets/c.png",
        '.cpp': "Assets/cplus.png",
        '.jpg': "Assets/jpg.png",
        '.png': "Assets/png.png",
        '.js': "Assets/js.png",
        '.xlsx': "Assets/xlsx.png",
        '.pdf': "Assets/pdf.png",
        # Add more file extensions and icon paths as needed
    }
    # Return the corresponding icon path, or a default icon path if not found
    return icon_paths.get(ext, 'Assets/python.png')

# Function to open selected file
def open_selected_file(event):
    global current_file_path, file_content_changed
    selection = file_list.selection()  # Retrieve the selected item
    if selection:
        selected_item = file_list.item(selection)['text']
        # Split the selected item text to get the filename without leading spaces
        selected_file = os.path.join(os.getcwd(), selected_item.strip())
        if os.path.isfile(selected_file):  # Check if selected item is a file
            try:
                with open(selected_file, 'r', encoding='utf-8') as file:
                    code_editor.delete(1.0, tk.END)
                    code_editor.insert(tk.END, file.read())
                current_file_path = selected_file
                update_line_numbers()
                file_content_changed = False  # Reset the flag indicating file changes
                apply_syntax_highlighting()
            except Exception as e:
                show_message(f"Error opening file: {e}")

# Function to get options on right click
def show_context_menu(event):
    context_menu = tk.Menu(root, tearoff=0)

    # Retrieve the item under the mouse cursor
    item_id = file_list.identify_row(event.y)
    if item_id:
        context_menu.add_command(label="Open in Code Editor", command=lambda: open_selected_file(None))
        context_menu.add_command(label="Rename", command=rename_file)
        context_menu.add_command(label="Delete", command=delete_file)

    context_menu.post(event.x_root, event.y_root)

# Function to rename the selected file
def rename_file():
    selection = file_list.selection()  # Retrieve the selected item
    if selection:
        selected_item = file_list.item(selection)['text']
        selected_file = os.path.join(os.getcwd(), selected_item.strip())
        new_name = simpledialog.askstring("Rename File", "Enter new name:", initialvalue=selected_item.strip())
        if new_name:
            try:
                if os.path.exists(selected_file):  # Check if the file exists
                    os.rename(selected_file, os.path.join(os.path.dirname(selected_file), new_name))
                    populate_file_list(file_list, path=".")  # Pass the file_list argument here
                else:
                    show_message(f"File '{selected_item}' does not exist.")
            except Exception as e:
                show_message(f"Error renaming file: {e}")

# Function to delete a file
def delete_file():
    selection = file_list.selection()  # Retrieve the selected item
    if selection:
        selected_item = file_list.item(selection)['text']
        selected_file = os.path.join(os.getcwd(), selected_item.strip())
        confirm = messagebox.askyesno("Delete File", f"Are you sure you want to delete {selected_file}?")
        if confirm:
            try:
                os.remove(selected_file)
                populate_file_list(file_list, path=".")  # Pass the file_list argument here
            except Exception as e:
                show_message(f"Error deleting file: {e}")


def apply_syntax_highlighting():
    code = code_editor.get(1.0, tk.END)
    clear_syntax_highlighting()

    if current_file_path:
        file_name, file_extension = os.path.splitext(current_file_path)

        if file_extension == '.py':
            apply_python_syntax_highlighting(code)
        elif file_extension == '.cpp' or file_extension == '.c':
            apply_cpp_c_syntax_highlighting(code)
        elif file_extension == '.js':
            apply_js_syntax_highlighting(code)

def clear_syntax_highlighting():
    code_editor.tag_remove('keyword', '1.0', tk.END)
    code_editor.tag_remove('string', '1.0', tk.END)
    code_editor.tag_remove('comment', '1.0', tk.END)

def apply_python_syntax_highlighting(code):
    keywords = r'\b(?:' + '|'.join(['def', 'class', 'for', 'if', 'else', 'elif', 'while', 'break', 'continue',
                                    'return', 'True', 'False', 'None', 'and', 'or', 'not', 'in', 'import', 'as',
                                    'from', 'try', 'except', 'finally', 'raise', 'assert', 'with', 'pass', 'lambda']) + r')\b'
    strings = r'\".*?\"'
    comments = r'#.*?$'
    patterns = {
        'keyword': keywords,
        'string': strings,
        'comment': comments
    }

    for tag, pattern in patterns.items():
        for match in re.finditer(pattern, code, re.MULTILINE | re.DOTALL):
            start = match.start()
            end = match.end()
            code_editor.tag_add(tag, f'1.0+{start}c', f'1.0+{end}c')

    code_editor.tag_config('keyword', foreground='blue')
    code_editor.tag_config('string', foreground='green')
    code_editor.tag_config('comment', foreground='gray')

def apply_cpp_c_syntax_highlighting(code):
    keywords = r'\b(?:' + '|'.join(['for', 'if', 'else', 'while', 'break', 'continue',
                                    'return', 'true', 'false', 'nullptr', 'and', 'or', 'not', 'in', 'import', 'as',
                                    'from', 'try', 'except', 'finally', 'raise', 'assert', 'with', 'pass']) + r')\b'
    strings = r'\".*?\"'
    comments = r'\/\/.*?$|\/\*(?:.|\n)*?\*\/'
    patterns = {
        'keyword': keywords,
        'string': strings,
        'comment': comments
    }

    for tag, pattern in patterns.items():
        for match in re.finditer(pattern, code, re.MULTILINE | re.DOTALL):
            start = match.start()
            end = match.end()
            code_editor.tag_add(tag, f'1.0+{start}c', f'1.0+{end}c')

    code_editor.tag_config('keyword', foreground='blue')
    code_editor.tag_config('string', foreground='green')
    code_editor.tag_config('comment', foreground='gray')

def apply_js_syntax_highlighting(code):
    keywords = r'\b(?:' + '|'.join(['var', 'function', 'for', 'if', 'else', 'while', 'break', 'continue',
                                    'return', 'true', 'false', 'null', 'new', 'typeof', 'instanceof', 'this', 'throw',
                                    'try', 'catch', 'finally', 'with', 'class', 'const', 'let', 'import', 'export']) + r')\b'
    strings = r'\".*?\"'
    comments = r'\/\/.*?$|\/\*(?:.|\n)*?\*\/'
    patterns = {
        'keyword': keywords,
        'string': strings,
        'comment': comments
    }

    for tag, pattern in patterns.items():
        for match in re.finditer(pattern, code, re.MULTILINE | re.DOTALL):
            start = match.start()
            end = match.end()
            code_editor.tag_add(tag, f'1.0+{start}c', f'1.0+{end}c')

    code_editor.tag_config('keyword', foreground='blue')
    code_editor.tag_config('string', foreground='green')
    code_editor.tag_config('comment', foreground='gray')

def share_code():
    if current_file_path:
        code_to_share = code_editor.get(1.0, tk.END)
        share_window = tk.Toplevel(root)
        share_window.title("Share Code")

        code_text = tk.Text(share_window)
        code_text.insert(tk.END, code_to_share)
        code_text.pack(fill=tk.BOTH, expand=True)

        # Create a frame to hold the buttons
        button_frame = tk.Frame(share_window)
        button_frame.pack(fill=tk.BOTH, expand=True)

        share_button = ttk.Button(button_frame, text="Copy to Clipboard",
                                  command=lambda: copy_to_clipboard(code_to_share))
        share_button.grid(row=0, column=0, padx=5, pady=5)

        whatsapp_button = ttk.Button(button_frame, text="Share via WhatsApp",
                                     command=lambda: share_via_whatsapp(code_to_share))
        whatsapp_button.grid(row=1, column=0, padx=5, pady=5)

        # Configure column 0 of the button frame to center its contents
        button_frame.columnconfigure(0, weight=1)

    else:
        show_message("No file selected to share.")

def copy_to_clipboard(code):
    root.clipboard_clear()
    root.clipboard_append(code)
    root.update()

def share_via_whatsapp(code):
    # Replace 'your_message' with the desired message you want to share along with the code
    message = f"Check out this code:\n{code}"
    # Replace 'your_whatsapp_number' with the phone number you want to share the code with (include the country code)
    whatsapp_url = f"https://wa.me/whatsappphonenumber/?text={message}"
    webbrowser.open(whatsapp_url)

# Code editor RIGHT-CLICK options
def show_editor_context_menu(event):
    # Create a context menu
    context_menu = Menu(root, tearoff=0)

    # Add options to the context menu
    context_menu.add_command(label="Select All", command=select_all)
    context_menu.add_separator() # Add a separator
    context_menu.add_command(label="Cut", command=cut)
    context_menu.add_command(label="Copy", command=copy)
    context_menu.add_command(label="Paste", command=paste)
    context_menu.add_separator()
    context_menu.add_command(label="Find All References", command=find_all_references)
    context_menu.add_command(label="Change All Occurrences", command=change_all_occurrences)
    context_menu.add_separator()
    context_menu.add_command(label="Format Document", command=format_document)

    # Display the context menu at the mouse position
    try:
        context_menu.tk_popup(event.x_root, event.y_root)
    finally:
        context_menu.grab_release()

def select_all():
    code_editor.tag_add("sel", "1.0", "end")

def copy():
    # Get the current cursor position (line.column)
    cursor_position = code_editor.index(tk.INSERT)
    # Extract the line number
    line_number = int(cursor_position.split(".")[0])
    # Find the start and end positions of the current line
    line_start = f"{line_number}.0"
    line_end = f"{line_number + 1}.0"
    # Copy the text of the current line to the clipboard
    code_editor.clipboard_clear()
    code_editor.clipboard_append(code_editor.get(line_start, line_end))

def cut():
    # Get the current cursor position (line.column)
    cursor_position = code_editor.index(tk.INSERT)
    # Extract the line number
    line_number = int(cursor_position.split(".")[0])
    # Find the start and end positions of the current line
    line_start = f"{line_number}.0"
    line_end = f"{line_number + 1}.0"
    # Cut the text of the current line
    code_editor.clipboard_clear()
    code_editor.clipboard_append(code_editor.get(line_start, line_end))
    code_editor.delete(line_start, line_end)


def paste():
    code_editor.event_generate("<<Paste>>")

def find_all_references():
    # Get the word to search for from the user
    word_to_search = simpledialog.askstring("Find All References", "Enter the word to search for:")
    if word_to_search:
        # Clear previous search highlighting
        code_editor.tag_remove('search', '1.0', tk.END)
        # Find all occurrences of the word
        start_pos = '1.0'
        while True:
            start_pos = code_editor.search(r'\m' + re.escape(word_to_search) + r'\M', start_pos, stopindex=tk.END, regexp=True)
            if not start_pos:
                break
            end_pos = f"{start_pos}+{len(word_to_search)}c"
            # Highlight the found word
            code_editor.tag_add('search', start_pos, end_pos)
            code_editor.tag_config('search', background='yellow')  # Configuring the tag to highlight in yellow
            # Move to the next occurrence
            start_pos = end_pos


def change_all_occurrences():
    # Create a new window for find/replace functionality
    root1 = tk.Toplevel(root)
    root1.title('Find/Replace')
    root1.geometry('450x250+500+200')
    root1.resizable(0, 0)

    # Create a LabelFrame inside the new window
    labelFrame = ttk.LabelFrame(root1, text='Find/Replace')
    labelFrame.pack(pady=50)

    # Add entry fields for find and replace
    findLabel = ttk.Label(labelFrame, text='Find:')
    findLabel.grid(row=0, column=0, padx=5, pady=5)
    findEntryField = ttk.Entry(labelFrame)
    findEntryField.grid(row=0, column=1, padx=5, pady=5)

    replaceLabel = ttk.Label(labelFrame, text='Replace:')
    replaceLabel.grid(row=1, column=0, padx=5, pady=5)
    replaceEntryField = ttk.Entry(labelFrame)
    replaceEntryField.grid(row=1, column=1, padx=5, pady=5)

    # Create a button to perform find and replace
    changeButton = ttk.Button(labelFrame, text='Change All', command=lambda: perform_find_replace(findEntryField.get(), replaceEntryField.get()))
    changeButton.grid(row=2, columnspan=2, padx=5, pady=5)

    # Function to perform find and replace
    def perform_find_replace(find_text, replace_text):
        # Clear previous search highlighting
        code_editor.tag_remove('search', '1.0', tk.END)
        # Find and replace all occurrences of the word
        start_pos = '1.0'
        while True:
            start_pos = code_editor.search(r'\m' + re.escape(find_text) + r'\M', start_pos, stopindex=tk.END,regexp=True)
            if not start_pos:
                break
            end_pos = f"{start_pos}+{len(find_text)}c"
            # Replace the found word with the replacement word
            code_editor.delete(start_pos, end_pos)
            code_editor.insert(start_pos, replace_text)
            # Move to the next occurrence
            start_pos = end_pos


# Format the entire code
def format_document():
    global code_editor

    # Store the current cursor position
    cursor_pos = code_editor.index(tk.INSERT)

    # Get the current code from the code editor
    code = code_editor.get("1.0", tk.END)

    # Determine the file extension
    file_extension = os.path.splitext(current_file_path)[1]

    # Use different formatters based on the file extension
    if file_extension == '.py':
        formatted_code = autopep8.fix_code(code)
    elif file_extension in ['.c', '.cpp']:
        # Apply formatting for C/C++ code
        formatted_code = subprocess.run(['clang-format', '-style=file'], input=code, text=True, capture_output=True).stdout
    elif file_extension == '.js':
        # Apply formatting for JavaScript code
        formatted_code = subprocess.run(['js-beautify', '-'], input=code, text=True, capture_output=True).stdout
    else:
        # If the file extension is not supported, do nothing
        return

    # Delete the existing code and insert the formatted code
    code_editor.delete("1.0", tk.END)
    code_editor.insert("1.0", formatted_code)

    # Restore the cursor position
    code_editor.mark_set(tk.INSERT, cursor_pos)
    code_editor.see(cursor_pos)

    # Reapply syntax highlighting
    apply_syntax_highlighting()

# Highlight Matching Brackets
def highlight_matching_brackets(event=None):
    global code_editor

    # Get the cursor position
    cursor_pos = code_editor.index(tk.INSERT)
    line, column = map(int, cursor_pos.split('.'))

    # Retrieve the character under the cursor
    char_under_cursor = code_editor.get(cursor_pos)

    # Clear previous bracket highlights
    code_editor.tag_remove('matching_bracket', '1.0', tk.END)

    if char_under_cursor == '}':
        # Search backward to find the opening bracket '{'
        opening_bracket_pos = find_opening_bracket(cursor_pos)
        if opening_bracket_pos:
            # Highlight the matching brackets
            code_editor.tag_add('matching_bracket', opening_bracket_pos, opening_bracket_pos + '+1c')
            code_editor.tag_add('matching_bracket', cursor_pos, cursor_pos + '+1c')
            code_editor.tag_config('matching_bracket', background='lightblue')
    elif char_under_cursor == '{':
        # Search forward to find the closing bracket '}'
        closing_bracket_pos = find_closing_bracket(cursor_pos)
        if closing_bracket_pos:
            # Highlight the matching brackets
            code_editor.tag_add('matching_bracket', cursor_pos, cursor_pos + '+1c')
            code_editor.tag_add('matching_bracket', closing_bracket_pos, closing_bracket_pos + '+1c')
            code_editor.tag_config('matching_bracket', background='lightblue')


def find_opening_bracket(position):
    while position:
        # Move one character back
        position = code_editor.index(f'{position} - 1 char')

        # Get the character at the current position
        char = code_editor.get(position)

        if char == '{':
            return position


def find_closing_bracket(position):
    while position:
        # Move one character forward
        position = code_editor.index(f'{position} + 1 char')

        # Get the character at the current position
        char = code_editor.get(position)

        if char == '}':
            return position


# Define a function to open the preferences dialog
def open_preferences():
    # Create a new window for the preferences dialog
    preferences_window = tk.Toplevel(root)
    preferences_window.title("Preferences")

    # Create a frame for preferences options
    preferences_frame = ttk.Frame(preferences_window)
    preferences_frame.pack(padx=10, pady=10)

    # Create Spinbox for font size
    font_size_label = ttk.Label(preferences_frame, text="Font Size:")
    font_size_label.grid(row=0, column=0, padx=5, pady=5)
    font_size_spinbox = ttk.Spinbox(preferences_frame, from_=8, to=72)
    font_size_spinbox.grid(row=0, column=1, padx=5, pady=5)

    # Create Combobox for font family
    font_family_label = ttk.Label(preferences_frame, text="Font Family:")
    font_family_label.grid(row=1, column=0, padx=5, pady=5)
    font_family_combobox = ttk.Combobox(preferences_frame, values=families())
    font_family_combobox.grid(row=1, column=1, padx=5, pady=5)

    # Create Spinbox for tab space
    tab_space_label = ttk.Label(preferences_frame, text="Tab Space:")
    tab_space_label.grid(row=2, column=0, padx=5, pady=5)
    tab_space_spinbox = ttk.Spinbox(preferences_frame, from_=1, to=8)
    tab_space_spinbox.grid(row=2, column=1, padx=5, pady=5)

    # Function to set preferences
    def set_preferences():
        # Get the selected values from the widgets
        selected_font_size = int(font_size_spinbox.get() or 12)  # Default to 12 if no value is provided
        selected_font_family = font_family_combobox.get() or "Arial"  # Default to "Arial" if no value is provided
        selected_tab_space = int(tab_space_spinbox.get() or 4)  # Default to 4 if no value is provided

        # Apply the selected preferences to the code editor
        code_editor.config(font=(selected_font_family, selected_font_size))
        code_editor.config(tabs=(selected_tab_space * selected_font_size))  # Set the tab width

    # Create a "Set" button
    set_button = ttk.Button(preferences_frame, text="Set", command=set_preferences)
    set_button.grid(row=3, columnspan=2, padx=5, pady=5)


# MAIN GUI BEGINS

# Create main window
root = tk.Tk()
root.title("Mini Code Editor")

p1 = tk.PhotoImage(file="Assets/code.png")

# Setting icon of master window
root.iconphoto(True, p1)

# Create ttkbootstrap style
style = Style(theme='minty')

# Create frames for different sections

# Create the frame for customization options
customization_frame = ttk.Frame(root, width=800, height=100)
customization_frame.pack(side=tk.TOP, fill=tk.X)

file_explorer_frame = ttk.Frame(root, width=80, height=400)
file_explorer_frame.pack(side=tk.LEFT, fill=tk.Y)

code_editor_frame = ttk.Frame(root, width=800, height=300)
code_editor_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
code_editor_frame.pack_propagate(0)  # Prevent the frame from expanding

terminal_frame = ttk.Frame(root, width=800, height=200)
terminal_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

# Add widgets to each frame

# Create a Treeview widget
file_list = ttk.Treeview(file_explorer_frame, selectmode="browse", columns=("Name", "Icon"))
file_list.pack(fill=tk.BOTH, expand=True)
file_list.heading("#0", text="Files")
file_list.column("#0", width=100)
file_list.column("Icon", width=10)  # Adjust the width of the icon column as needed

# Call the populate_file_list function to populate the file list initially
populate_file_list(file_list, path=".")  # Pass the file_list argument here

# Configure the Treeview to show icons
style = ttk.Style()
style.configure("Treeview", highlightthickness=0, bd=0)
style.map("Treeview", background=[('selected', '#0078d7')])
style.configure("Treeview.Heading", background="Lightgrey", foreground="Black")
style.configure("Treeview", foreground="black")
style.configure("Treeview.Item", foreground="black")

# Associate icon images with Treeview
file_list.icon_images = {"text": tk.PhotoImage(file="Assets/c.png"),
                         "image": tk.PhotoImage(file="Assets/c.png"),
                         "default": tk.PhotoImage(file="Assets/c.png")}

file_list.bind("<Double-Button-1>", open_selected_file)
file_list.bind("<Button-3>", show_context_menu)
file_list.bind("<<TreeviewContextMenu>>", show_context_menu)

# CUTOMIZATION FRAME LEFT SIDE

# Add buttons to customization frame

# Create the hamburger menu button
hamburger_menu = ttk.Menubutton(customization_frame, text="☰")
hamburger_menu.pack(side=tk.LEFT, padx=3, pady=3)

# Create the menu for the hamburger menu button
menu = tk.Menu(hamburger_menu, tearoff=0)
hamburger_menu.configure(menu=menu)

# Apply ttkbootstrap style to the menu options
style = Style(theme='minty')  # Choose your preferred theme from ttkbootstrap
menu_style = ttk.Style()
menu_style.configure("TMenubutton", font=('Helvetica', 10))  # Increase font size

# Add menu items for "Open Folder", "Open File", and "New File"
menu.add_command(label="Open Folder", command=open_folder)
menu.add_command(label="Open File", command=open_file)
menu.add_command(label="New File", command=new_file)

share_button = ttk.Button(customization_frame, text="Share", command=share_code)
share_button.pack(side=tk.LEFT, padx=5, pady=5)

save_button = ttk.Button(customization_frame, text="Save File", command=save_file)
save_button.pack(side=tk.LEFT, padx=5, pady=5)

# Apply the custom style to the Run button
run_button = ttk.Button(customization_frame, text="Run", command=run_code, style='Success.TButton')
run_button.pack(side=tk.LEFT, padx=5, pady=5)

# Create a checkbox for autosave
autosave_enabled = tk.BooleanVar()
autosave_checkbox = ttk.Checkbutton(customization_frame, text="Autosave", variable=autosave_enabled)
autosave_checkbox.pack(side=tk.LEFT, padx=5, pady=5)

# Bind functions to code editor
code_editor = tk.Text(code_editor_frame)
code_editor.bind("<KeyRelease>", lambda event: apply_syntax_highlighting())
code_editor.bind("<Button-3>", show_editor_context_menu)

# Bind text change and cursor movement events to the highlight_matching_brackets function
code_editor.bind("<KeyRelease>", highlight_matching_brackets)
code_editor.bind("<Motion>", highlight_matching_brackets)


code_editor.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)


# CUTOMIZATION FRAME RIGHT SIDE

# Add a "Preferences" button to the right of the existing buttons in the customization frame
preferences_button = ttk.Button(customization_frame, text="Preferences", command=open_preferences)
preferences_button.pack(side=tk.RIGHT, padx=5, pady=5)

# Create a frame for line numbers
line_numbers_frame = tk.Frame(code_editor_frame, width=40)
line_numbers_frame.pack(side=tk.LEFT, fill=tk.Y)

line_numbers = tk.Text(line_numbers_frame, width=2, padx=5, pady=2, wrap="none", state="disabled", bg='lightgray')
line_numbers.pack(fill=tk.Y)

# Bind text editor scrolling to line numbers
code_editor.bind("<MouseWheel>", lambda event: line_numbers.yview_scroll(-1 * int(event.delta / 120), "units"))
line_numbers.bind("<MouseWheel>", lambda event: code_editor.yview_scroll(-1 * int(event.delta / 120), "units"))

# Bind text editor scrolling to line numbers
code_editor.bind("<Button-4>", lambda event: line_numbers.yview_scroll(-1, "units"))
code_editor.bind("<Button-5>", lambda event: line_numbers.yview_scroll(1, "units"))

code_editor.bind("<Key>", update_line_numbers)

terminal = tk.Text(terminal_frame)
terminal.configure(bg="black", fg="yellow", state="disabled")
terminal.pack(fill=tk.BOTH, expand=True)

# Flag to track autosave status
autosave_enabled.set(False)

root.mainloop()
