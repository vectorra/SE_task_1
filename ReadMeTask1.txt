Singleton and Multiton in Python

This project demonstrates how to implement two common design patterns using metaclasses:

- **Singleton**: Ensures only one instance of a class exists.
- **Multiton**: Allows a limited number of instances (based on keys), with automatic reuse or fallback.

## Features

- Singleton class reuses the same instance every time.
- Multiton class creates new instances for unique keys up to a fixed limit (`COUNT`).
- Once the limit is reached, further requests reuse an existing instance.

## How to Run

bash
python singleton_multiton.py
