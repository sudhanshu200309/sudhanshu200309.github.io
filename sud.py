
# Method 5: Using two-pointer approach
def reverse_string_two_pointer(s):
    """Reverse a string using two pointers"""
    s_list = list(s)  # Convert to list for mutability
    left, right = 0, len(s_list) - 1
    
    while left < right:
        s_list[left], s_list[right] = s_list[right], s_list[left]
        left += 1
        right -= 1
    
    return "".join(s_list)


# Test all methods
if __name__ == "__main__":
    test_string = "Hello, World!"
    print(f"Two-pointer method: {reverse_string_two_pointer(test_string)}")
