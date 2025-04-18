import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from tkinterdnd2 import TkinterDnD, DND_FILES
from PIL import Image, ImageTk, ImageDraw
import os
import threading
from datetime import datetime
from PIL import ImageFont
from tkinter import simpledialog
from Code.extractors import Extractor
import sys

try:
    from bertopic import BERTopic
    from keybert import KeyBERT
    AI_ENABLED = True
except ImportError:
    AI_ENABLED = False

class NeoExplorerPro(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.root = self 
        self.title("NeoExplorer Pro 2025")
        self.geometry("1400x800")
        self.minsize(1100, 700)
        self.dark_mode = False 

        # Modern color scheme
        self.colors = {
            'dark': {
                'bg': '#1a1a2e',
                'card': '#16213e',
                'text': '#e6f1ff',
                'accent': '#4cc9f0',
                'secondary': '#4895ef',
                'highlight': '#7209b7',
                'tree_bg': '#1e1e2e',
                'tree_fg': '#ffffff',
                'tree_select': '#3a3a5a'
            },
            'light': {
                'bg': '#f8f9fa',
                'card': '#ffffff',
                'text': '#212529',
                'accent': '#4361ee',
                'secondary': '#3a0ca3',
                'highlight': '#f72585',
                'tree_bg': '#ffffff',
                'tree_fg': '#000000',
                'tree_select': '#e0e0e0'
            }
        }

        # Notebook (tab container)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True)

        # Create the analysis tab as a Frame
        self.analysis_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.analysis_tab, text="AI Analysis")
        self.setup_ai_tab()

        # App state
        self.dark_mode = True
        self.current_dir = os.path.expanduser("~")
        self.history = []
        self.history_index = -1
        self.selected_files = []

        # Create modern UI
        self.setup_ui()
        self.setup_file_list()
        # Load initial directory
        self.load_directory(self.current_dir)
    def setup_file_list(self):
        """Setup the file list (Treeview) and its components"""
        self.file_list = ttk.Treeview(self.main_container, columns=("Name", "Size", "Type", "Modified"), show="headings")
        self.file_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Configure columns
        self.file_list.heading("Name", text="Name", command=lambda: self.sort_column("Name", False))
        self.file_list.heading("Size", text="Size", command=lambda: self.sort_column("Size", False))
        self.file_list.heading("Type", text="Type", command=lambda: self.sort_column("Type", False))
        self.file_list.heading("Modified", text="Modified", command=lambda: self.sort_column("Modified", False))

        self.file_list.column("Name", width=300, anchor="w")
        self.file_list.column("Size", width=100, anchor="e")
        self.file_list.column("Type", width=100, anchor="center")
        self.file_list.column("Modified", width=160, anchor="center")

        # Add scrollbar
        file_list_scroll = ttk.Scrollbar(self.main_container, orient="vertical", command=self.file_list.yview)
        file_list_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_list.configure(yscrollcommand=file_list_scroll.set)
    
    def setup_ui(self):
        """Setup modern UI components"""
        self.configure_theme()

         # Main container
        self.main_container = ttk.Frame(self)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        # Navigation bar
        self.setup_navbar()
        
        # Main content area
        self.setup_main_content()
        
        # Status bar
        self.setup_statusbar()
        
        # Context menu
        self.setup_context_menu()
        
        # Enable drag and drop
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.handle_drop)

    def configure_theme(self):
        """Configure theme colors and styles"""
        theme = self.colors['dark' if self.dark_mode else 'light']
        
        self.configure(bg=theme['bg'])
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure styles
        self.style.configure('.', background=theme['bg'], foreground=theme['text'])
        self.style.configure('TFrame', background=theme['bg'])
        self.style.configure('TLabel', background=theme['bg'], foreground=theme['text'])
        self.style.configure('TButton', 
                           background=theme['accent'],
                           foreground=theme['text'],
                           borderwidth=0,
                           focuscolor=theme['secondary'])
        self.style.map('TButton',
                     background=[('active', theme['secondary']),
                               ('disabled', '#555555')])
        self.style.configure('Treeview', 
                           background=theme['tree_bg'],
                           foreground=theme['tree_fg'],
                           fieldbackground=theme['tree_bg'],
                           rowheight=25)
        self.style.map('Treeview',
                     background=[('selected', theme['tree_select'])])
        self.style.configure('Treeview.Heading', 
                           background=theme['secondary'],
                           foreground=theme['text'],
                           relief='flat')
        self.style.configure('TNotebook', background=theme['bg'])
        self.style.configure('TNotebook.Tab', 
                           background=theme['card'],
                           foreground=theme['text'],
                           padding=[10, 5])
        self.style.map('TNotebook.Tab',
                     background=[('selected', theme['accent'])])
        self.style.configure('TEntry', fieldbackground=theme['card'])
        self.style.configure('TCombobox', fieldbackground=theme['card'])

    def setup_navbar(self):
        """Modern navigation bar"""
        theme = self.colors['dark' if self.dark_mode else 'light']
        
        navbar = ttk.Frame(self.main_container)
        navbar.pack(fill=tk.X, pady=(0, 10))
        
        # Navigation buttons
        nav_buttons = [
            ('⬅', self.go_back),
            ('➡', self.go_forward),
            ('⬆', self.go_up),
            ('🔄', self.refresh)
        ]
        
        for text, cmd in nav_buttons:
            btn = ttk.Button(navbar, text=text, command=cmd, width=3)
            btn.pack(side=tk.LEFT, padx=2)
        
        # Path display
        self.path_var = tk.StringVar()
        path_entry = ttk.Entry(navbar, textvariable=self.path_var, width=60)
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        path_entry.bind('<Return>', lambda e: self.load_directory(self.path_var.get()))
        
        # Search bar
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(navbar, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=(0, 10))
        search_entry.bind('<KeyRelease>', self.do_search)
        search_entry.insert(0, "Search...")
        search_entry.bind('<FocusIn>', lambda e: search_entry.delete(0, tk.END) if search_entry.get() == "Search..." else None)
        search_entry.bind('<FocusOut>', lambda e: search_entry.insert(0, "Search...") if not search_entry.get() else None)
        
        # Theme toggle
        theme_btn = ttk.Button(navbar, text="🌙" if self.dark_mode else "☀", 
                             command=self.toggle_theme)
        theme_btn.pack(side=tk.RIGHT)

    def setup_main_content(self):
        """Setup modern main content area with folder tree and preview"""
        theme = self.colors['dark' if self.dark_mode else 'light']
        
        # Main content frame
        content_frame = ttk.Frame(self.main_container)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Split view - left panel for tree, right for preview
        paned_window = ttk.PanedWindow(content_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Treeview
        left_panel = ttk.Frame(paned_window, width=250)
        paned_window.add(left_panel, weight=0)
        
        # Treeview for folder navigation
        self.tree = ttk.Treeview(left_panel, show='tree')
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add scrollbar
        tree_scroll = ttk.Scrollbar(left_panel, orient='vertical', command=self.tree.yview)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        
        # Populate initial drives
        self.populate_initial_tree()
        self.tree.bind('<<TreeviewOpen>>', self.on_tree_open)
        self.tree.bind('<Double-1>', self.on_tree_double_click)
        
        # Right panel - Preview/Content
        right_panel = ttk.Frame(paned_window)
        paned_window.add(right_panel, weight=1)
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(right_panel)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Preview tab
        self.preview_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.preview_tab, text='Preview')
        
        # Content text area with scrollbar
        self.content_text = scrolledtext.ScrolledText(
            self.preview_tab,
            wrap=tk.WORD,
            bg=theme['card'],
            fg=theme['text'],
            insertbackground=theme['text'],
            selectbackground=theme['highlight']
        )
        self.content_text.pack(fill=tk.BOTH, expand=True)
        
        # Drag and drop support
        self.content_text.drop_target_register(DND_FILES)
        self.content_text.dnd_bind('<<Drop>>', self.handle_file_drop)
        
        # Analysis tab (if AI enabled)
        if AI_ENABLED:
            self.setup_ai_tab()

    def handle_file_drop(self, event):
        """Handle files dropped on the text area"""
        file_paths = event.data.split() if isinstance(event.data, str) else [event.data]
        
        self.content_text.delete(1.0, tk.END)
        extractor = Extractor()
        
        for file_path in file_paths:
            file_path = file_path.strip('{}')  # Remove curly braces if present
            
            if not os.path.exists(file_path):
                self.content_text.insert(tk.END, f"File not found: {file_path}\n\n")
                continue
                
            try:
                mime_type = extractor.detect_mime_type(file_path)
                extractor_func = extractor.get_extractor_by_mime_type(mime_type)

                if extractor_func:
                    content = extractor_func(file_path)
                else:
                    content = f"Unsupported file type: {mime_type}"

                # Truncate content if too long
                content = extractor.truncate_text(content, 10000)
                self.content_text.insert(tk.END, f"=== {os.path.basename(file_path)} ===\n\n{content}\n\n")

            except Exception as e:
                self.content_text.insert(tk.END, f"=== {os.path.basename(file_path)} ===\n\nError reading file: {str(e)}\n\n")
        
        self.notebook.select(self.preview_tab)
    def populate_initial_tree(self):
        """Populate initial tree with drives and common folders"""
        # Add drives
        drives = [f"{d}:\\" for d in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if os.path.exists(f"{d}:\\")]
        for drive in drives:
            node = self.tree.insert('', 'end', text=drive, values=(drive,), open=False)
            # Add dummy node to make it expandable
            self.tree.insert(node, 'end')
        
        # Add special folders
        special_folders = {
            'Desktop': os.path.expanduser('~/Desktop'),
            'Documents': os.path.expanduser('~/Documents'),
            'Downloads': os.path.expanduser('~/Downloads'),
            'Pictures': os.path.expanduser('~/Pictures')
        }
        
        for name, path in special_folders.items():
            if os.path.exists(path):
                node = self.tree.insert('', 'end', text=name, values=(path,), open=False)
                if any(os.path.isdir(os.path.join(path, item)) for item in os.listdir(path)):
                    self.tree.insert(node, 'end')  # Dummy node

    def on_tree_open(self, event):
        """Handle tree node expansion"""
        node = self.tree.focus()
        path = self.tree.item(node, 'values')[0]
        
        # Remove dummy node if exists
        children = self.tree.get_children(node)
        if children and not self.tree.item(children[0], 'values'):
            self.tree.delete(children[0])
            self.populate_tree_node(node, path)

    def populate_tree_node(self, parent_node, path):
        """Populate tree node with subdirectories"""
        try:
            for item in os.listdir(path):
                full_path = os.path.join(path, item)
                if os.path.isdir(full_path):
                    node = self.tree.insert(parent_node, 'end', text=item, values=(full_path,), open=False)
                    # Add dummy node if has subdirectories
                    if any(os.path.isdir(os.path.join(full_path, sub)) for sub in os.listdir(full_path)):
                        self.tree.insert(node, 'end')
        except Exception as e:
            print(f"Error reading directory {path}: {e}")

    def on_tree_double_click(self, event):
        """Handle double click on tree node"""
        node = self.tree.focus()
        path = self.tree.item(node, 'values')[0]
        if path and os.path.isdir(path):
            self.load_directory(path)

    def setup_ai_tab(self):
        """Setup AI analysis tab"""
        theme = self.colors['dark' if self.dark_mode else 'light']
        
        # Topics frame
        topics_frame = ttk.LabelFrame(self.analysis_tab, text="Key Topics")
        topics_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.topics_text = scrolledtext.ScrolledText(
            topics_frame,
            wrap=tk.WORD,
            height=10,
            bg=theme['card'],
            fg=theme['text']
        )
        self.topics_text.pack(fill=tk.BOTH, expand=True)
        
        # Keywords frame
        keywords_frame = ttk.LabelFrame(self.analysis_tab, text="Keywords")
        keywords_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.keywords_text = scrolledtext.ScrolledText(
            keywords_frame,
            wrap=tk.WORD,
            height=10,
            bg=theme['card'],
            fg=theme['text']
        )
        self.keywords_text.pack(fill=tk.BOTH, expand=True)
        
        # Analyze button
        analyze_btn = ttk.Button(
            self.analysis_tab,
            text="Analyze Content",
            command=self.analyze_content
        )
        analyze_btn.pack(pady=5)

    def setup_statusbar(self):
        """Modern status bar"""
        theme = self.colors['dark' if self.dark_mode else 'light']
        
        statusbar = ttk.Frame(self.main_container)
        statusbar.pack(fill=tk.X, pady=(5, 0))
        
        self.status_label = ttk.Label(statusbar, text='Ready')
        self.status_label.pack(side=tk.LEFT)
        
        # File count
        self.file_count_label = ttk.Label(statusbar, text='0 items')
        self.file_count_label.pack(side=tk.RIGHT, padx=10)

    def setup_context_menu(self):
        """Modern context menu"""
        self.context_menu = tk.Menu(self, tearoff=0)
        
        actions = [
            ('Open', self.open_selected),
            ('Scan Text', self.scan_text),
            ('---', None),
            ('Copy', self.copy_files),
            ('Paste', self.paste_files),
            ('---', None),
            ('Delete', self.delete_files),
            ('Rename', self.rename_file),
            ('---', None),
            ('Properties', self.show_properties)
        ]
        
        for label, cmd in actions:
            if label == '---':
                self.context_menu.add_separator()
            else:
                self.context_menu.add_command(label=label, command=cmd)
        
        if AI_ENABLED:
            self.context_menu.add_separator()
            self.context_menu.add_command(label='Analyze with AI', command=self.analyze_content)
        
        # Bind to both tree and file list
        self.tree.bind('<Button-3>', self.show_context_menu)
        self.file_list.bind('<Button-3>', self.show_context_menu)

    def show_context_menu(self, event):
        """Show context menu at mouse position"""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def load_directory(self, directory):
        """Load directory contents into file list"""
        if os.path.isdir(directory):
            self.current_dir = directory
            self.path_var.set(directory)
            
            # Update history
            if self.history_index == -1 or self.history[self.history_index] != directory:
                self.history = self.history[:self.history_index+1]
                self.history.append(directory)
                self.history_index += 1
            
            self.update_file_list()
        else:
            messagebox.showerror("Error", f"{directory} is not a valid directory.")

    def update_file_list(self):
        """Update file list with current directory contents"""
        for item in self.file_list.get_children():
            self.file_list.delete(item)
        
        try:
            # Add ".." for parent directory
            parent_dir = os.path.dirname(self.current_dir)
            if parent_dir != self.current_dir:  # Not at root
                self.file_list.insert('', 'end', values=('..', '', 'Parent Directory', ''), tags=('parent',))
            
            # Add files and folders
            for file_name in sorted(os.listdir(self.current_dir), key=str.lower):
                full_path = os.path.join(self.current_dir, file_name)
                
                if os.path.isdir(full_path):
                    file_type = 'Folder'
                    size = ''
                else:
                    file_type = 'File'
                    size = self.format_size(os.path.getsize(full_path))
                
                modified_time = datetime.fromtimestamp(os.path.getmtime(full_path)).strftime('%Y-%m-%d %H:%M:%S')
                
                self.file_list.insert('', 'end', values=(file_name, size, file_type, modified_time))
            
            self.file_count_label.config(text=f"{len(self.file_list.get_children())} items")
            self.status_label.config(text=f"Loaded {self.current_dir}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Could not load directory: {str(e)}")

    def format_size(self, size):
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

    def sort_column(self, col, reverse):
        """Sort treeview by column"""
        data = [(self.file_list.set(child, col), child) 
               for child in self.file_list.get_children('')]
        
        # Handle numeric sorting for size column
        if col == 'size':
            def key_func(item):
                val = item[0]
                if val.endswith(' KB'):
                    return float(val[:-3]) * 1024
                elif val.endswith(' MB'):
                    return float(val[:-3]) * 1024 * 1024
                elif val.endswith(' GB'):
                    return float(val[:-3]) * 1024 * 1024 * 1024
                elif val.endswith(' TB'):
                    return float(val[:-3]) * 1024 * 1024 * 1024 * 1024
                elif val.endswith(' B'):
                    return float(val[:-2])
                return 0
            data.sort(key=key_func, reverse=reverse)
        else:
            data.sort(reverse=reverse)
        
        for index, (val, child) in enumerate(data):
            self.file_list.move(child, '', index)
        
        self.file_list.heading(col, command=lambda: self.sort_column(col, not reverse))

    def on_file_select(self, event):
        """Handle file selection change"""
        self.selected_files = [self.file_list.item(item, 'values')[0] 
                             for item in self.file_list.selection()]
        
        if len(self.selected_files) == 1:
            self.preview_selected_file()

    def preview_selected_file(self):
        """Preview content of selected file"""
        if not self.selected_files:
            return
            
        file_name = self.selected_files[0]
        file_path = os.path.join(self.current_dir, file_name)
        
        if os.path.isdir(file_path):
            self.content_text.delete(1.0, tk.END)
            self.content_text.insert(tk.END, f"Folder: {file_name}\n\nDouble-click to open")
            return
        
        # Try to read text files
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(5000)  # Read first 5000 characters
                self.content_text.delete(1.0, tk.END)
                self.content_text.insert(tk.END, f"File: {file_name}\n\n{content}")
                if len(content) == 5000:
                    self.content_text.insert(tk.END, "\n\n... (content truncated)")
        except:
            self.content_text.delete(1.0, tk.END)
            self.content_text.insert(tk.END, f"File: {file_name}\n\nBinary file or unsupported format")
    
    def scan_text(self):
        """Scan and display text content from selected files using Extractor"""
        if not self.selected_files:
            messagebox.showwarning("Warning", "No files selected")
            return
            
        self.content_text.delete(1.0, tk.END)
        extractor = Extractor()

        for file_name in self.selected_files:
            file_path = os.path.join(self.current_dir, file_name)

            if os.path.isdir(file_path):
                continue

            try:
                mime_type = extractor.detect_mime_type(file_path)
                extractor_func = extractor.get_extractor_by_mime_type(mime_type)

                if extractor_func:
                    content = extractor_func(file_path)
                else:
                    content = f"Unsupported file type: {mime_type}"

                # Truncate content if too long
                content = extractor.truncate_text(content, 10000)
                self.content_text.insert(tk.END, f"=== {file_name} ===\n\n{content}\n\n")

            except Exception as e:
                self.content_text.insert(tk.END, f"=== {file_name} ===\n\nError reading file: {str(e)}\n\n")

        self.notebook.select(self.preview_tab)

    def analyze_content(self):
        """Analyze text content with AI"""
        if not AI_ENABLED:
            messagebox.showwarning("Warning", "AI features not available (required packages not installed)")
            return
            
        if not self.selected_files:
            messagebox.showwarning("Warning", "No files selected")
            return
            
        # Get content from selected files
        content = ""
        for file_name in self.selected_files:
            file_path = os.path.join(self.current_dir, file_name)
            
            if os.path.isdir(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content += f.read(10000) + "\n\n"  # Read first 10000 characters
            except:
                continue
        
        if not content:
            messagebox.showwarning("Warning", "No readable text content found")
            return
            
        # Show loading message
        self.topics_text.delete(1.0, tk.END)
        self.keywords_text.delete(1.0, tk.END)
        self.topics_text.insert(tk.END, "Analyzing topics...")
        self.keywords_text.insert(tk.END, "Extracting keywords...")
        self.notebook.select(self.analysis_tab)
        self.update()
        
        # Run analysis in background thread
        threading.Thread(target=self.run_ai_analysis, args=(content,), daemon=True).start()

    def run_ai_analysis(self, content):
        """Run AI analysis in background thread"""
        try:
            # Extract keywords
            kw_model = KeyBERT()
            keywords = kw_model.extract_keywords(content, keyphrase_ngram_range=(1, 2), stop_words='english')
            
            # Extract topics
            topic_model = BERTopic()
            topics, _ = topic_model.fit_transform([content])
            
            # Update UI with results
            self.after(0, self.display_ai_results, keywords, topic_model.get_topic_info())
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", f"AI analysis failed: {str(e)}"))

    def display_ai_results(self, keywords, topic_info):
        """Display AI analysis results"""
        # Display keywords
        self.keywords_text.delete(1.0, tk.END)
        for keyword, score in keywords:
            self.keywords_text.insert(tk.END, f"- {keyword} (confidence: {score:.2f})\n")
        
        # Display topics
        self.topics_text.delete(1.0, tk.END)
        for _, row in topic_info.iterrows():
            if row['Topic'] != -1:  # Skip outliers
                self.topics_text.insert(tk.END, f"Topic {row['Topic']}: {row['Name']}\n")
                self.topics_text.insert(tk.END, f"  Keywords: {row['Representation']}\n\n")

    def open_selected(self):
        """Open selected file or directory"""
        if not self.selected_files:
            return
            
        file_name = self.selected_files[0]
        file_path = os.path.join(self.current_dir, file_name)
        
        if file_name == '..':
            parent_dir = os.path.dirname(self.current_dir)
            self.load_directory(parent_dir)
        elif os.path.isdir(file_path):
            self.load_directory(file_path)
        else:
            try:
                os.startfile(file_path)  # Windows
            except:
                try:
                    # Try other OS methods
                    import subprocess
                    opener = "open" if sys.platform == "darwin" else "xdg-open"
                    subprocess.call([opener, file_path])
                except:
                    messagebox.showerror("Error", f"Could not open {file_name}")

    def go_back(self):
        """Navigate back in history"""
        if self.history_index > 0:
            self.history_index -= 1
            self.load_directory(self.history[self.history_index])

    def go_forward(self):
        """Navigate forward in history"""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.load_directory(self.history[self.history_index])

    def go_up(self):
        """Navigate to parent directory"""
        parent_dir = os.path.dirname(self.current_dir)
        self.load_directory(parent_dir)

    def refresh(self):
        """Refresh current directory"""
        self.load_directory(self.current_dir)

    def do_search(self, event):
        """Filter files based on search query"""
        search_query = self.search_var.get().lower()
        
        if not search_query or search_query == "search...":
            for item in self.file_list.get_children():
                self.file_list.item(item, tags=())
            return
            
        for item in self.file_list.get_children():
            file_name = self.file_list.item(item, 'values')[0].lower()
            if search_query in file_name:
                self.file_list.item(item, tags=('match',))
                self.file_list.see(item)
            else:
                self.file_list.item(item, tags=())

    def copy_files(self):
        """Copy selected files to clipboard"""
        if not self.selected_files:
            return
            
        self.clipboard_files = []
        for file_name in self.selected_files:
            self.clipboard_files.append(os.path.join(self.current_dir, file_name))
        
        messagebox.showinfo("Info", f"Copied {len(self.clipboard_files)} items to clipboard")

    def paste_files(self):
        """Paste files from clipboard"""
        if not hasattr(self, 'clipboard_files') or not self.clipboard_files:
            return
            
        for src_path in self.clipboard_files:
            try:
                dst_path = os.path.join(self.current_dir, os.path.basename(src_path))
                if os.path.exists(dst_path):
                    # Handle duplicate names
                    base, ext = os.path.splitext(dst_path)
                    counter = 1
                    while os.path.exists(f"{base} ({counter}){ext}"):
                        counter += 1
                    dst_path = f"{base} ({counter}){ext}"
                
                if os.path.isdir(src_path):
                    import shutil
                    shutil.copytree(src_path, dst_path)
                else:
                    import shutil
                    shutil.copy2(src_path, dst_path)
                
            except Exception as e:
                messagebox.showerror("Error", f"Could not paste {os.path.basename(src_path)}: {str(e)}")
        
        self.refresh()

    def delete_files(self):
        """Delete selected files"""
        if not self.selected_files:
            return
            
        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete {len(self.selected_files)} selected items?",
            parent=self
        )
        
        if not confirm:
            return
            
        for file_name in self.selected_files:
            file_path = os.path.join(self.current_dir, file_name)
            try:
                if os.path.isdir(file_path):
                    import shutil
                    shutil.rmtree(file_path)
                else:
                    os.remove(file_path)
            except Exception as e:
                messagebox.showerror("Error", f"Could not delete {file_name}: {str(e)}")
        
        self.refresh()

    def rename_file(self):
        """Rename selected file"""
        if not self.selected_files or len(self.selected_files) > 1:
            return
            
        old_name = self.selected_files[0]
        old_path = os.path.join(self.current_dir, old_name)
        
        new_name = simpledialog.askstring(
            "Rename",
            f"Rename '{old_name}' to:",
            initialvalue=old_name,
            parent=self
        )
        
        if new_name and new_name != old_name:
            new_path = os.path.join(self.current_dir, new_name)
            try:
                os.rename(old_path, new_path)
                self.refresh()
            except Exception as e:
                messagebox.showerror("Error", f"Could not rename file: {str(e)}")

    def show_properties(self):
        """Show properties of selected file"""
        if not self.selected_files or len(self.selected_files) > 1:
            return
            
        file_name = self.selected_files[0]
        file_path = os.path.join(self.current_dir, file_name)
        
        try:
            stats = os.stat(file_path)
            size = self.format_size(stats.st_size)
            modified = datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            created = datetime.fromtimestamp(stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
            
            properties = f"Name: {file_name}\n"
            properties += f"Path: {file_path}\n"
            properties += f"Type: {'Folder' if os.path.isdir(file_path) else 'File'}\n"
            properties += f"Size: {size}\n"
            properties += f"Created: {created}\n"
            properties += f"Modified: {modified}\n"
            
            messagebox.showinfo("Properties", properties)
        except Exception as e:
            messagebox.showerror("Error", f"Could not get properties: {str(e)}")

    def handle_drop(self, event):
        """Handle files dropped on window"""
        file_path = event.data.strip()
        if os.path.isdir(file_path):
            self.load_directory(file_path)
        else:
            self.load_directory(os.path.dirname(file_path))

    def toggle_theme(self):
        """Toggle between dark and light theme"""
        self.dark_mode = not self.dark_mode
        self.configure_theme()
        
        # Update text widget colors
        theme = self.colors['dark' if self.dark_mode else 'light']
        self.content_text.config(
            bg=theme['card'],
            fg=theme['text'],
            insertbackground=theme['text'],
            selectbackground=theme['highlight']
        )
        
        if AI_ENABLED:
            self.topics_text.config(
                bg=theme['card'],
                fg=theme['text']
            )
            self.keywords_text.config(
                bg=theme['card'],
                fg=theme['text']
            )

if __name__ == "__main__":
    app = NeoExplorerPro()
    app.mainloop()