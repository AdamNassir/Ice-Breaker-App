# Hello World

```python
def factorial(number):
    """Return the factorial of a non-negative integer recursively."""
    if number < 0:
        raise ValueError("number must be non-negative")
    if number <= 1:
        return 1
    return number * factorial(number - 1)
```
