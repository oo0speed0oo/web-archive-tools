#!/usr/bin/env python3
"""
PDF Splitter
-----------
Split a large PDF into multiple smaller PDFs based on page ranges.
Define which pages go into which files using an interactive GUI.

SETUP (run once):
    pip install PyPDF2

USAGE:
    python pdf_splitter.py

A GUI will let you:
1. Select a PDF file
2. Define page ranges for each output file
3. Name each output PDF
4. Split and save
"""

import os
from tkinter import Tk, filedialog, messagebox, Button, Label, Frame, Entry, Listbox, Scrollbar
from tkinter import END
import PyPDF2


class PDFSplitterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Splitter")
        self.root.geometry("600x550")
        self.root.configure(bg="#ffffff")
        self.root.resizable(False, False)
        self.root.attributes('-topmost', True)

        self.pdf_path = None
        self.total_pages = 0
        self.splits = []  # List of (output_name, page_range_str)

        self.setup_ui()

    def setup_ui(self):
        """Create the GUI layout."""
        # Title
        Label(
            self.root,
            text="PDF Splitter",
            font=("Arial", 16, "bold"),
            fg="#000000",
            bg="#ffffff"
        ).pack(pady=10)

        # File selection frame
        file_frame = Frame(self.root, bg="#f0f0f0")
        file_frame.pack(pady=10, padx=20, fill="x")

        Label(
            file_frame,
            text="PDF File:",
            font=("Arial", 11),
            fg="#000000",
            bg="#f0f0f0"
        ).pack(side="left", padx=5)

        self.file_label = Label(
            file_frame,
            text="No file selected",
            font=("Arial", 10),
            fg="#666666",
            bg="#f0f0f0"
        )
        self.file_label.pack(side="left", padx=5, fill="x", expand=True)

        Button(
            file_frame,
            text="Select PDF",
            font=("Arial", 10, "bold"),
            bg="#4CAF50",
            fg="white",
            activebackground="#45a049",
            activeforeground="white",
            relief="raised",
            bd=2,
            command=self.select_pdf
        ).pack(side="right", padx=5)

        # Info label
        self.info_label = Label(
            self.root,
            text="",
            font=("Arial", 10),
            fg="#666666",
            bg="#ffffff"
        )
        self.info_label.pack(pady=5)

        # Splits section
        Label(
            self.root,
            text="Define PDF Splits (e.g., 1-5, 6-10, 11-20):",
            font=("Arial", 11, "bold"),
            fg="#000000",
            bg="#ffffff"
        ).pack(pady=(10, 5), padx=20, anchor="w")

        # Input frame for new split
        input_frame = Frame(self.root, bg="#ffffff")
        input_frame.pack(pady=5, padx=20, fill="x")

        Label(
            input_frame,
            text="Name:",
            font=("Arial", 10),
            fg="#000000",
            bg="#ffffff"
        ).pack(side="left", padx=5)

        self.name_entry = Entry(
            input_frame,
            font=("Arial", 10),
            width=20
        )
        self.name_entry.pack(side="left", padx=5)

        Label(
            input_frame,
            text="Pages:",
            font=("Arial", 10),
            fg="#000000",
            bg="#ffffff"
        ).pack(side="left", padx=5)

        self.pages_entry = Entry(
            input_frame,
            font=("Arial", 10),
            width=15
        )
        self.pages_entry.pack(side="left", padx=5)

        Button(
            input_frame,
            text="Add Split",
            font=("Arial", 10, "bold"),
            bg="#2196F3",
            fg="white",
            activebackground="#0b7dda",
            activeforeground="white",
            relief="raised",
            bd=2,
            command=self.add_split
        ).pack(side="left", padx=5)

        # Listbox to show splits
        Label(
            self.root,
            text="Splits to create:",
            font=("Arial", 10),
            fg="#000000",
            bg="#ffffff"
        ).pack(pady=(10, 5), padx=20, anchor="w")

        list_frame = Frame(self.root, bg="#ffffff")
        list_frame.pack(pady=5, padx=20, fill="both", expand=True)

        scrollbar = Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        self.splits_listbox = Listbox(
            list_frame,
            font=("Arial", 10),
            fg="#000000",
            bg="#ffffff",
            yscrollcommand=scrollbar.set,
            height=8
        )
        self.splits_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.splits_listbox.yview)

        # Remove button
        Button(
            self.root,
            text="Remove Selected",
            font=("Arial", 10, "bold"),
            bg="#FF9800",
            fg="white",
            activebackground="#e68900",
            activeforeground="white",
            relief="raised",
            bd=2,
            command=self.remove_split
        ).pack(pady=5)

        # Action buttons
        button_frame = Frame(self.root, bg="#ffffff")
        button_frame.pack(pady=10, fill="x")

        Button(
            button_frame,
            text="Split PDF",
            font=("Arial", 12, "bold"),
            width=12,
            bg="#4CAF50",
            fg="white",
            activebackground="#45a049",
            activeforeground="white",
            relief="raised",
            bd=3,
            command=self.split_pdf
        ).pack(side="left", padx=5)

        Button(
            button_frame,
            text="Split All",
            font=("Arial", 12, "bold"),
            width=12,
            bg="#FF9800",
            fg="white",
            activebackground="#e68900",
            activeforeground="white",
            relief="raised",
            bd=3,
            command=self.split_all_pages
        ).pack(side="left", padx=5)

        Button(
            button_frame,
            text="Clear All",
            font=("Arial", 12, "bold"),
            width=12,
            bg="#f44336",
            fg="white",
            activebackground="#da190b",
            activeforeground="white",
            relief="raised",
            bd=3,
            command=self.clear_all
        ).pack(side="right", padx=5)

    def select_pdf(self):
        """Open file dialog to select PDF."""
        file_path = filedialog.askopenfilename(
            title="Select PDF file",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )

        if file_path:
            self.pdf_path = file_path
            self.file_label.config(text=os.path.basename(file_path))

            # Get total page count
            try:
                with open(file_path, "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    self.total_pages = len(reader.pages)
                    self.info_label.config(
                        text=f"Total pages: {self.total_pages}",
                        fg="#4CAF50"
                    )
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read PDF: {e}")

    def add_split(self):
        """Add a new split definition."""
        if not self.pdf_path:
            messagebox.showwarning("Warning", "Please select a PDF first")
            return

        name = self.name_entry.get().strip()
        pages = self.pages_entry.get().strip()

        if not name or not pages:
            messagebox.showwarning("Warning", "Enter both name and page range")
            return

        # Validate page range format
        try:
            validate_page_range(pages, self.total_pages)
        except ValueError as e:
            messagebox.showerror("Invalid Range", str(e))
            return

        self.splits.append((name, pages))
        self.splits_listbox.insert(END, f"{name}: pages {pages}")

        # Clear inputs
        self.name_entry.delete(0, END)
        self.pages_entry.delete(0, END)
        self.name_entry.focus()

    def remove_split(self):
        """Remove selected split from list."""
        selection = self.splits_listbox.curselection()
        if selection:
            idx = selection[0]
            self.splits_listbox.delete(idx)
            del self.splits[idx]

    def clear_all(self):
        """Clear all splits."""
        self.splits.clear()
        self.splits_listbox.delete(0, END)

    def split_pdf(self):
        """Split the PDF based on defined ranges."""
        if not self.pdf_path:
            messagebox.showwarning("Warning", "Please select a PDF first")
            return

        if not self.splits:
            messagebox.showwarning("Warning", "Define at least one split")
            return

        output_dir = os.path.dirname(self.pdf_path)

        try:
            with open(self.pdf_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)

                for output_name, page_range in self.splits:
                    writer = PyPDF2.PdfWriter()

                    # Parse page range
                    pages = parse_page_range(page_range)

                    # Add pages to writer
                    for page_num in pages:
                        if 1 <= page_num <= len(reader.pages):
                            writer.add_page(reader.pages[page_num - 1])

                    # Save output PDF
                    output_path = os.path.join(output_dir, f"{output_name}.pdf")
                    with open(output_path, "wb") as out_f:
                        writer.write(out_f)

                    print(f"✓ Created: {output_name}.pdf")

            messagebox.showinfo("Success", f"Split {len(self.splits)} PDF(s) successfully!")
            self.clear_all()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to split PDF: {e}")

    def split_all_pages(self):
        """Split PDF into one file per page."""
        if not self.pdf_path:
            messagebox.showwarning("Warning", "Please select a PDF first")
            return

        output_dir = os.path.dirname(self.pdf_path)

        try:
            with open(self.pdf_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                total = len(reader.pages)

                for page_num in range(1, total + 1):
                    writer = PyPDF2.PdfWriter()
                    writer.add_page(reader.pages[page_num - 1])

                    # Simple names: page1.pdf, page2.pdf, etc.
                    output_name = f"page{page_num}"
                    output_path = os.path.join(output_dir, f"{output_name}.pdf")

                    with open(output_path, "wb") as out_f:
                        writer.write(out_f)

                    print(f"✓ Created: {output_name}.pdf")

            messagebox.showinfo("Success", f"Split into {total} PDF file(s)!")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to split PDF: {e}")


def parse_page_range(range_str: str) -> list:
    """Parse page range string like '1-5,7,9-11' into list of page numbers."""
    pages = []
    parts = range_str.split(",")

    for part in parts:
        part = part.strip()
        if "-" in part:
            start, end = part.split("-")
            start, end = int(start.strip()), int(end.strip())
            pages.extend(range(start, end + 1))
        else:
            pages.append(int(part))

    return sorted(set(pages))  # Remove duplicates and sort


def validate_page_range(range_str: str, total_pages: int) -> None:
    """Validate that page range is valid."""
    try:
        pages = parse_page_range(range_str)
        if not pages:
            raise ValueError("No pages specified")
        if any(p < 1 or p > total_pages for p in pages):
            raise ValueError(f"Page numbers must be between 1 and {total_pages}")
    except ValueError as e:
        raise ValueError(f"Invalid page range: {e}")


def main():
    root = Tk()
    root.attributes('-topmost', True)
    app = PDFSplitterGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
