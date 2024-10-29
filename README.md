# IDS706 Python vs Rust
![CI Status](https://github.com/YitaoS/ids706_mini_project2/actions/workflows/ci.yml/badge.svg)

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Rust (with `cargo` and `rustup` installed)
- Docker (if using DevContainer)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/YitaoS/ids706_mini_project2.git
   cd ids706_mini_project2
   ```

2. **Install Python dependencies**:
   ```bash
   make install
   ```

   This will upgrade `pip` and install the necessary dependencies for development.

3. **Install Rust dependencies**:
   If you don’t already have Rust installed, you can install it using `rustup`:
   ```bash
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   rustup update
   ```
   Once installed, you can navigate to the Rust project directory and build it:
   ```bash
   cd rust_version/polling_places_analysis
   cargo build --release
   ```

4. **Optional: Build the development environment using DevContainer**:
   - Open the project in Visual Studio Code.
   - Run **Reopen in Container** from the Command Palette (`Ctrl + Shift + P` or `Cmd + Shift + P`).

### Usage

- **Run the Python main script**:
  ```bash
  make run
  ```

- **Run the Rust project**:
  ```bash
  cd rust_version/polling_places_analysis
  cargo run --release
  ```

- **Run tests**:
  ```bash
  make test
  ```

- **Format the code** using `black` (for Python) and `rustfmt` (for Rust):
  ```bash
  make format
  ```

- **Lint the Python code** using `flake8`:
  ```bash
  make lint
  ```

- **Deploy reports and images**:
  ```bash
  make deploy
  ```

### Additional Commands

- **Check code formatting** (without applying changes):
  ```bash
  make check-format
  ```

- **Clean up `.pyc` files, `__pycache__` directories, and Rust build artifacts**:
  ```bash
  make clean
  ```

- **Run the full CI process (linting, testing, and formatting check)**:
  ```bash
  make ci
  ```

### CI/CD Status
Continuous Integration (CI) checks are automatically run using GitHub Actions. You can view the current status by looking at the badge at the top of this file.

### Contributing

Feel free to fork the repository and submit pull requests for improvements or bug fixes. Ensure your changes pass the linting and test suites before submission.
