import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image
import threading
from pathlib import Path
import time
import queue
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing
from collections import defaultdict

class ImageCompressorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Compressor - Optimized")
        self.root.geometry("700x500")
        self.root.resizable(True, True)
        
        # Variables
        self.selected_directory = tk.StringVar()
        self.compression_quality = tk.IntVar(value=85)
        self.max_workers = tk.IntVar(value=min(4, multiprocessing.cpu_count()))
        self.min_file_size = tk.IntVar(value=50)  # KB
        self.is_processing = False
        self.total_images = 0
        self.processed_images = 0
        self.update_queue = queue.Queue()
        
        # Performance tracking
        self.start_time = None
        self.stats = defaultdict(int)
        
        self.setup_ui()
        self.start_queue_processor()
        
    def setup_ui(self):
        # Main frame with scrollable content
        canvas = tk.Canvas(self.root)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        main_frame = ttk.Frame(scrollable_frame, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        main_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # Directory selection
        ttk.Label(main_frame, text="Select Directory:", font=('TkDefaultFont', 10, 'bold')).grid(row=row, column=0, sticky=tk.W, pady=(0, 5))
        row += 1
        
        dir_frame = ttk.Frame(main_frame)
        dir_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        dir_frame.columnconfigure(0, weight=1)
        
        self.dir_entry = ttk.Entry(dir_frame, textvariable=self.selected_directory, width=60)
        self.dir_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(dir_frame, text="Browse", command=self.browse_directory).grid(row=0, column=1)
        row += 1
        
        # Performance Settings Frame
        perf_frame = ttk.LabelFrame(main_frame, text="Performance Settings", padding="10")
        perf_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        perf_frame.columnconfigure(1, weight=1)
        row += 1
        
        # Worker threads
        ttk.Label(perf_frame, text="Worker Threads:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        worker_frame = ttk.Frame(perf_frame)
        worker_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        self.worker_scale = ttk.Scale(
            worker_frame, 
            from_=1, 
            to=multiprocessing.cpu_count(), 
            orient=tk.HORIZONTAL, 
            variable=self.max_workers,
            length=200
        )
        self.worker_scale.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        self.worker_label = ttk.Label(worker_frame, text=str(self.max_workers.get()))
        self.worker_label.grid(row=0, column=1)
        self.worker_scale.configure(command=self.update_worker_label)
        
        # Minimum file size filter
        ttk.Label(perf_frame, text="Min File Size (KB):").grid(row=1, column=0, sticky=tk.W, pady=(5, 5))
        size_frame = ttk.Frame(perf_frame)
        size_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(5, 5))
        
        ttk.Entry(size_frame, textvariable=self.min_file_size, width=10).grid(row=0, column=0, padx=(0, 5))
        ttk.Label(size_frame, text="(Skip files smaller than this)").grid(row=0, column=1, sticky=tk.W)
        
        # Compression quality
        ttk.Label(perf_frame, text="Compression Quality:").grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        quality_frame = ttk.Frame(perf_frame)
        quality_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(5, 0))
        quality_frame.columnconfigure(0, weight=1)
        
        self.quality_scale = ttk.Scale(
            quality_frame, 
            from_=1, 
            to=100, 
            orient=tk.HORIZONTAL, 
            variable=self.compression_quality,
            length=200
        )
        self.quality_scale.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        self.quality_label = ttk.Label(quality_frame, text="85")
        self.quality_label.grid(row=0, column=1)
        self.quality_scale.configure(command=self.update_quality_label)
        
        # Statistics Frame
        stats_frame = ttk.LabelFrame(main_frame, text="Statistics", padding="10")
        stats_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        stats_frame.columnconfigure(1, weight=1)
        row += 1
        
        self.stats_labels = {}
        stats_info = [
            ("Images Found:", "images_found"),
            ("Processing Speed:", "speed"),
            ("Space Saved:", "space_saved"),
            ("Time Elapsed:", "time_elapsed")
        ]
        
        for i, (label_text, key) in enumerate(stats_info):
            ttk.Label(stats_frame, text=label_text).grid(row=i, column=0, sticky=tk.W, pady=2)
            self.stats_labels[key] = ttk.Label(stats_frame, text="--")
            self.stats_labels[key].grid(row=i, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Progress section
        ttk.Label(main_frame, text="Progress:", font=('TkDefaultFont', 10, 'bold')).grid(row=row, column=0, sticky=tk.W, pady=(10, 5))
        row += 1
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            main_frame, 
            variable=self.progress_var, 
            maximum=100,
            length=500
        )
        self.progress_bar.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        row += 1
        
        self.progress_label = ttk.Label(main_frame, text="Ready to compress images...")
        self.progress_label.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        row += 1
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=(10, 0))
        row += 1
        
        self.start_button = ttk.Button(
            button_frame, 
            text="Start Compression", 
            command=self.start_compression,
            style="Accent.TButton"
        )
        self.start_button.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_button = ttk.Button(
            button_frame, 
            text="Stop", 
            command=self.stop_compression,
            state=tk.DISABLED
        )
        self.stop_button.grid(row=0, column=1, padx=(0, 10))
        
        ttk.Button(button_frame, text="Clear Log", command=self.clear_log).grid(row=0, column=2, padx=(0, 10))
        ttk.Button(button_frame, text="Exit", command=self.root.quit).grid(row=0, column=3)
        
        # Status text area
        ttk.Label(main_frame, text="Log:", font=('TkDefaultFont', 10, 'bold')).grid(row=row, column=0, sticky=tk.W, pady=(20, 5))
        row += 1
        
        # Text widget with scrollbar
        text_frame = ttk.Frame(main_frame)
        text_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 0))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        self.log_text = tk.Text(text_frame, height=10, wrap=tk.WORD, font=('Consolas', 9))
        log_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
    def update_worker_label(self, value):
        self.worker_label.config(text=str(int(float(value))))
        
    def update_quality_label(self, value):
        self.quality_label.config(text=str(int(float(value))))
        
    def clear_log(self):
        self.log_text.delete(1.0, tk.END)
        
    def browse_directory(self):
        directory = filedialog.askdirectory(title="Select Directory with Images")
        if directory:
            self.selected_directory.set(directory)
            self.log_message(f"Selected directory: {directory}")
            
    def start_queue_processor(self):
        """Process GUI updates from background threads"""
        try:
            while True:
                update_type, data = self.update_queue.get_nowait()
                
                if update_type == "log":
                    self.log_message(data)
                elif update_type == "progress":
                    progress, label_text = data
                    self.progress_var.set(progress)
                    self.progress_label.config(text=label_text)
                elif update_type == "stats":
                    self.update_stats_display(data)
                    
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.start_queue_processor)  # Check every 100ms
            
    def log_message(self, message):
        """Add message to log with timestamp"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        
        # Limit log size to prevent memory issues
        lines = int(self.log_text.index('end-1c').split('.')[0])
        if lines > 1000:  # Keep only last 1000 lines
            self.log_text.delete(1.0, f"{lines-1000}.0")
        
    def update_stats_display(self, stats):
        """Update statistics display"""
        self.stats_labels["images_found"].config(text=f"{stats.get('total_images', 0)}")
        
        if stats.get('processing_time', 0) > 0:
            speed = stats.get('processed_images', 0) / stats.get('processing_time', 1)
            self.stats_labels["speed"].config(text=f"{speed:.1f} images/sec")
        
        space_saved_mb = stats.get('total_saved', 0) / (1024 * 1024)
        self.stats_labels["space_saved"].config(text=f"{space_saved_mb:.2f} MB")
        
        elapsed = stats.get('processing_time', 0)
        self.stats_labels["time_elapsed"].config(text=f"{elapsed:.1f}s")
        
    def get_image_files(self, directory):
        """Get list of image files with filtering"""
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}
        min_size_bytes = self.min_file_size.get() * 1024
        
        image_files = []
        for root_dir, dirs, files in os.walk(directory):
            for file in files:
                if Path(file).suffix.lower() in image_extensions:
                    full_path = os.path.join(root_dir, file)
                    try:
                        if os.path.getsize(full_path) >= min_size_bytes:
                            image_files.append(full_path)
                    except OSError:
                        continue  # Skip files that can't be accessed
        
        return image_files
        
    def compress_single_image(self, image_path, quality):
        """Compress a single image - optimized version"""
        try:
            original_size = os.path.getsize(image_path)
            
            # Use context manager and optimize memory usage
            with Image.open(image_path) as img:
                # Skip if image is already very small
                if original_size < 10240:  # 10KB
                    return {
                        'path': image_path,
                        'success': True,
                        'original_size': original_size,
                        'new_size': original_size,
                        'saved_bytes': 0,
                        'error': None
                    }
                
                # Get original mode and size
                original_mode = img.mode
                original_format = img.format
                
                # Convert RGBA to RGB if saving as JPEG
                file_ext = Path(image_path).suffix.lower()
                if file_ext in ['.jpg', '.jpeg'] and original_mode == 'RGBA':
                    # Create white background
                    rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                    rgb_img.paste(img, mask=img.split()[-1] if len(img.split()) == 4 else None)
                    img = rgb_img
                
                # Optimize save parameters based on format
                save_kwargs = {'optimize': True}
                
                if file_ext in ['.jpg', '.jpeg']:
                    save_kwargs.update({
                        'format': 'JPEG',
                        'quality': quality,
                        'progressive': True
                    })
                elif file_ext == '.png':
                    save_kwargs.update({
                        'format': 'PNG',
                        'compress_level': 9
                    })
                elif file_ext == '.webp':
                    save_kwargs.update({
                        'format': 'WEBP',
                        'quality': quality,
                        'method': 6
                    })
                else:
                    # Convert unsupported formats to JPEG
                    new_path = str(Path(image_path).with_suffix('.jpg'))
                    save_kwargs.update({
                        'format': 'JPEG',
                        'quality': quality,
                        'progressive': True
                    })
                    img.save(new_path, **save_kwargs)
                    if new_path != image_path:
                        os.remove(image_path)
                        image_path = new_path
                
                # If not converting format, save with current format
                if file_ext in ['.jpg', '.jpeg', '.png', '.webp']:
                    img.save(image_path, **save_kwargs)
            
            new_size = os.path.getsize(image_path)
            saved_bytes = original_size - new_size
            
            return {
                'path': image_path,
                'success': True,
                'original_size': original_size,
                'new_size': new_size,
                'saved_bytes': saved_bytes,
                'error': None
            }
            
        except Exception as e:
            return {
                'path': image_path,
                'success': False,
                'original_size': 0,
                'new_size': 0,
                'saved_bytes': 0,
                'error': str(e)
            }
            
    def compression_worker(self):
        """Optimized worker thread for image compression"""
        directory = self.selected_directory.get()
        quality = self.compression_quality.get()
        max_workers = int(self.max_workers.get())
        
        if not directory or not os.path.exists(directory):
            self.update_queue.put(("log", "Error: Please select a valid directory"))
            self.compression_finished()
            return
            
        # Get all image files
        self.update_queue.put(("log", "Scanning for images..."))
        image_files = self.get_image_files(directory)
        
        if not image_files:
            self.update_queue.put(("log", "No images found matching criteria"))
            self.compression_finished()
            return
            
        self.total_images = len(image_files)
        self.update_queue.put(("log", f"Found {self.total_images} images to process"))
        self.update_queue.put(("log", f"Using {max_workers} worker threads"))
        
        # Initialize statistics
        self.stats = {
            'total_images': self.total_images,
            'processed_images': 0,
            'successful': 0,
            'failed': 0,
            'total_saved': 0,
            'processing_time': 0
        }
        
        self.start_time = time.time()
        self.processed_images = 0
        
        # Process images using thread pool
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_path = {
                executor.submit(self.compress_single_image, img_path, quality): img_path 
                for img_path in image_files
            }
            
            # Process completed tasks
            batch_update_counter = 0
            for future in as_completed(future_to_path):
                if not self.is_processing:
                    # Cancel remaining futures
                    for f in future_to_path:
                        f.cancel()
                    break
                    
                result = future.result()
                self.processed_images += 1
                
                # Update statistics
                self.stats['processed_images'] = self.processed_images
                self.stats['processing_time'] = time.time() - self.start_time
                
                if result['success']:
                    self.stats['successful'] += 1
                    self.stats['total_saved'] += result['saved_bytes']
                    
                    # Log detailed results only for significant savings or errors
                    if result['saved_bytes'] > 1024:  # > 1KB saved
                        relative_path = os.path.relpath(result['path'], directory)
                        saved_percent = (result['saved_bytes'] / result['original_size'] * 100) if result['original_size'] > 0 else 0
                        if batch_update_counter % 10 == 0:  # Log every 10th file
                            self.update_queue.put(("log", f"Compressed {relative_path}: {saved_percent:.1f}% smaller"))
                else:
                    self.stats['failed'] += 1
                    relative_path = os.path.relpath(result['path'], directory)
                    self.update_queue.put(("log", f"Error processing {relative_path}: {result['error']}"))
                
                # Update progress (less frequently for better performance)
                batch_update_counter += 1
                if batch_update_counter % 5 == 0 or self.processed_images == self.total_images:
                    progress = (self.processed_images / self.total_images) * 100
                    progress_text = f"Progress: {self.processed_images}/{self.total_images} images processed"
                    self.update_queue.put(("progress", (progress, progress_text)))
                    self.update_queue.put(("stats", self.stats.copy()))
        
        # Final summary
        if self.is_processing:
            total_time = time.time() - self.start_time
            self.update_queue.put(("log", f"\nCompression completed in {total_time:.1f} seconds!"))
            self.update_queue.put(("log", f"Successfully processed: {self.stats['successful']} images"))
            self.update_queue.put(("log", f"Failed: {self.stats['failed']} images"))
            
            if self.stats['total_saved'] > 0:
                total_saved_mb = self.stats['total_saved'] / (1024 * 1024)
                avg_speed = self.stats['successful'] / total_time if total_time > 0 else 0
                self.update_queue.put(("log", f"Total space saved: {total_saved_mb:.2f} MB"))
                self.update_queue.put(("log", f"Average speed: {avg_speed:.1f} images/second"))
        else:
            self.update_queue.put(("log", "\nCompression stopped by user"))
            
        self.compression_finished()
        
    def start_compression(self):
        """Start the compression process"""
        if not self.selected_directory.get():
            messagebox.showerror("Error", "Please select a directory first")
            return
            
        self.is_processing = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress_var.set(0)
        
        # Reset statistics
        for label in self.stats_labels.values():
            label.config(text="--")
        
        # Start compression in separate thread
        self.compression_thread = threading.Thread(target=self.compression_worker, daemon=True)
        self.compression_thread.start()
        
    def stop_compression(self):
        """Stop the compression process"""
        self.is_processing = False
        self.update_queue.put(("log", "Stopping compression..."))
        
    def compression_finished(self):
        """Called when compression is finished"""
        self.is_processing = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.progress_label.config(text="Compression finished")

def main():
    # Set high DPI awareness for Windows
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
    
    root = tk.Tk()
    app = ImageCompressorGUI(root)
    
    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    # root.geometry(f"+{x}+{y}")
    root.geometry("720x800")

    root.mainloop()

if __name__ == "__main__":
    main()