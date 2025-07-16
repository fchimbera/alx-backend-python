# 📦 Unittests and Integration Tests Project

This project focuses on mastering two essential testing methodologies in Python: **unit tests** and **integration tests**. It is designed for **novice-level** developers and runs from **July 13, 2025 (11:00 PM)** to **July 20, 2025 (11:00 PM)**. The project includes an automated review system triggered at the deadline.

## 🧪 Testing Concepts

### ✅ Unit Tests
Unit testing ensures individual functions behave as expected given various inputs. These tests isolate function logic by:
- Testing standard inputs and edge cases
- Mocking all external dependencies like network/database calls
- Asking: _“If everything around this function works correctly, does this function work correctly?”_

### 🔄 Integration Tests
Integration tests verify full code pathways and inter-component interactions. These:
- Avoid unnecessary mocking, except for low-level external calls (HTTP requests, file/database I/O)
- Validate the interaction between modules, classes, and functions

## 🚀 How to Run Tests

Use the following command to execute your test scripts:

```bash
$ python -m unittest path/to/test_file.py
