class Car:
    """A class to represent a car."""
    
    def __init__(self, brand):
        """
        Initialize Car with brand.
        
        Args:
            brand: The car's brand/manufacturer
        """
        self.brand = brand
    
    def print_brand(self):
        """Print the car's brand."""
        print(f"Car Brand: {self.brand}")
    
    def __str__(self):
        """Return string representation of the car."""
        return f"Car({self.brand})"


# Example usage
if __name__ == "__main__":
    # Create car objects with different brands
    car1 = Car("Toyota")
    car1.print_brand()
    
    car2 = Car("BMW")
    car2.print_brand()
    
    car3 = Car("Tesla")
    car3.print_brand()
    
    # Using string representation
    print(f"\n{car1}")
    print(f"{car2}")
    print(f"{car3}")
