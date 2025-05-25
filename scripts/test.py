def star_rating_to_number(star_string):
    return star_string.count('★')

# Example usage
rating_str = "★★★☆☆"
numeric_rating = star_rating_to_number(rating_str)
print(numeric_rating)  # Output: 3
