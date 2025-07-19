"""
ReportLab Position Converter Module

Provides easy coordinate conversion for ReportLab canvas positioning using
percentages, inches, and millimeters instead of raw points.

Usage:
    from reportlab_position import PositionConverter
    from reportlab.lib.pagesizes import letter
    
    pos = PositionConverter(letter)
    canvas.drawString(pos.pct_w(20), pos.pct_h(80), "Hello World")
"""

from reportlab.lib.pagesizes import letter


class Point:
    """
    A 2D point that supports arithmetic operations for easy coordinate math.
    
    Can be used anywhere a (x, y) tuple is expected through tuple unpacking.
    """
    
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
    
    def __add__(self, other):
        """Add another Point or scalar to this Point."""
        if isinstance(other, Point):
            return Point(self.x + other.x, self.y + other.y)
        # Scalar addition
        return Point(self.x + other, self.y + other)
    
    def __sub__(self, other):
        """Subtract another Point or scalar from this Point."""
        if isinstance(other, Point):
            return Point(self.x - other.x, self.y - other.y)
        # Scalar subtraction
        return Point(self.x - other, self.y - other)
    
    def __mul__(self, scalar):
        """Multiply Point by a scalar."""
        return Point(self.x * scalar, self.y * scalar)
    
    def __truediv__(self, scalar):
        """Divide Point by a scalar."""
        return Point(self.x / scalar, self.y / scalar)
    
    def __iter__(self):
        """Allow tuple unpacking: x, y = point"""
        yield self.x
        yield self.y
    
    def __getitem__(self, index):
        """Allow indexing: point[0] = x, point[1] = y"""
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        else:
            raise IndexError("Point index out of range")
    
    def __repr__(self):
        return f"Point({self.x}, {self.y})"
    
    def __str__(self):
        return f"({self.x}, {self.y})"
    
    def tuple(self):
        """Explicitly convert to tuple if needed."""
        return (self.x, self.y)


class PositionConverter:
    """
    Convert percentage, inch, and millimeter values to ReportLab point coordinates.
    
    ReportLab uses points (1/72 inch) with origin at bottom-left (0,0).
    """
    
    # Constants for unit conversion
    POINTS_PER_INCH = 72
    MM_PER_INCH = 25.4
    POINTS_PER_MM = POINTS_PER_INCH / MM_PER_INCH
    
    def __init__(self, page_size=None):
        """
        Initialize with page size.
        
        Args:
            page_size: Tuple (width, height) in points. Defaults to letter size.
        """
        if page_size is None:
            page_size = letter
        self.width, self.height = page_size
    
    # Percentage methods
    def pct_w(self, percent):
        """Convert percentage of page width to points."""
        return (percent / 100.0) * self.width
    
    def pct_h(self, percent):
        """Convert percentage of page height to points."""
        return (percent / 100.0) * self.height
    
    def pct(self, w_percent, h_percent):
        """Convert percentage width and height to Point."""
        return Point(self.pct_w(w_percent), self.pct_h(h_percent))
    
    # Inch methods
    def in_w(self, inches):
        """Convert inches to points (for width positioning)."""
        return inches * self.POINTS_PER_INCH
    
    def in_h(self, inches):
        """Convert inches to points (for height positioning)."""
        return inches * self.POINTS_PER_INCH
    
    def inches(self, w_inches, h_inches):
        """Convert inch width and height to Point."""
        return Point(self.in_w(w_inches), self.in_h(h_inches))
    
    # Millimeter methods
    def mm_w(self, millimeters):
        """Convert millimeters to points (for width positioning)."""
        return millimeters * self.POINTS_PER_MM
    
    def mm_h(self, millimeters):
        """Convert millimeters to points (for height positioning)."""
        return millimeters * self.POINTS_PER_MM
    
    def mm(self, w_mm, h_mm):
        """Convert millimeter width and height to Point."""
        return Point(self.mm_w(w_mm), self.mm_h(h_mm))
    
    # Utility methods for common positions
    def center_w(self):
        """Get x-coordinate for horizontal center."""
        return self.width / 2
    
    def center_h(self):
        """Get y-coordinate for vertical center."""
        return self.height / 2
    
    def center(self):
        """Get Point for page center."""
        return Point(self.center_w(), self.center_h())
    
    def top(self, margin_percent=5):
        """Get y-coordinate near top of page with optional margin."""
        return self.pct_h(100 - margin_percent)
    
    def bottom(self, margin_percent=5):
        """Get y-coordinate near bottom of page with optional margin."""
        return self.pct_h(margin_percent)
    
    def left(self, margin_percent=5):
        """Get x-coordinate near left edge with optional margin."""
        return self.pct_w(margin_percent)
    
    def right(self, margin_percent=5):
        """Get x-coordinate near right edge with optional margin."""
        return self.pct_w(100 - margin_percent)
    
    # Properties for easy access to page dimensions
    @property
    def page_width(self):
        """Page width in points."""
        return self.width
    
    @property
    def page_height(self):
        """Page height in points."""
        return self.height
    
    @property
    def page_size(self):
        """Page size as Point."""
        return Point(self.width, self.height)


def _demo():
    """Example usage demonstration (run with python -c 'import module; module._demo()')"""
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter, A4
    
    # Example 1: Basic usage
    pos = PositionConverter(letter)
    print(f"20% width = {pos.pct_w(20)} points")
    print(f"80% height = {pos.pct_h(80)} points")
    print(f"1 inch = {pos.in_w(1)} points")
    print(f"25.4 mm = {pos.mm_w(25.4)} points")
    
    # Example 2: Point arithmetic
    center = pos.center()
    offset = pos.pct(10, 5)
    new_pos = center - offset  # Point subtraction!
    print(f"Center: {center}")
    print(f"Offset: {offset}")
    print(f"Center - 10%,5%: {new_pos}")
    
    # Example 3: Create a simple PDF
    c = canvas.Canvas("position_test.pdf", pagesize=letter)
    
    # Use percentage positioning
    c.drawString(*pos.pct(10, 90), "Top left area (10%, 90%)")
    
    # Point arithmetic in action
    x, y = pos.center() - pos.pct(15, 0)  # Tuple unpacking works!
    c.drawString(x, y, "Center minus 15% left")
    
    # Traditional positioning still works
    c.drawString(pos.pct_w(50), pos.pct_h(20), "Lower middle (50%, 20%)")
    
    # Complex positioning with arithmetic
    top_right = pos.pct(85, 85)
    slightly_left = top_right - pos.pct(5, 0)
    c.drawString(*slightly_left, "Near top-right")
    
    # Use inch positioning
    c.drawString(*pos.inches(1, 1), "1 inch from bottom-left")
    
    # Use millimeter positioning  
    c.drawString(*pos.mm(50, 200), "50mm right, 200mm up")
    
    c.save()
    print("Created position_test.pdf demonstrating coordinate conversions and Point arithmetic")


if __name__ == "__main__":
    _demo()
