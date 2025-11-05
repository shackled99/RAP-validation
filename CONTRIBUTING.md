# Contributing to RAP-validation

Thank you for your interest in contributing to the Recursive Attractor Principle validation framework! 🎯

## Ways to Contribute

### 1. New Domain Validations
We're actively seeking validation of RAP across different domains:
- **Cancer growth dynamics** (eukaryotic systems)
- **Market equilibria** (economic systems)
- **Stellar evolution** (cosmological systems)
- **Neural network training** (artificial systems)
- **Any recursive system** you think might show 85% convergence

### 2. Model Improvements
- Alternative formulations of the RAP equations
- Optimization of fitting algorithms
- Better handling of edge cases
- Performance improvements

### 3. Statistical Analysis
- Robustness checks
- Sensitivity analysis
- Alternative statistical tests
- Cross-validation methods

### 4. Documentation
- Tutorials and examples
- Code documentation improvements
- Theoretical explanations
- Use case demonstrations

## How to Contribute

### Reporting Issues
- Use the GitHub issue tracker
- Provide clear description of the problem
- Include reproducible examples when possible
- Specify your Python version and dependencies

### Submitting Changes

1. **Fork the repository**
   ```bash
   git clone https://github.com/shackled99/RAP-validation.git
   cd RAP-validation
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow the existing code style
   - Add comments and docstrings
   - Update documentation if needed

4. **Test your changes**
   - Ensure existing functionality still works
   - Add tests for new features

5. **Commit with clear messages**
   ```bash
   git commit -m "Add: Brief description of changes"
   ```

6. **Push and create a Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```

### Code Style Guidelines

- Follow PEP 8 for Python code
- Use descriptive variable names
- Add docstrings to all functions
- Include type hints where helpful
- Comment complex logic

**Example:**
```python
def calculate_convergence(trajectory, target, tolerance=0.05):
    """
    Check if trajectory converged to target value.
    
    Parameters:
    -----------
    trajectory : array-like
        Time series data
    target : float
        Target convergence value
    tolerance : float
        Acceptable deviation from target
    
    Returns:
    --------
    bool
        True if converged within tolerance
    """
    final_value = trajectory[-1]
    return abs(final_value - target) < tolerance
```

## Domain Validation Guidelines

If you're validating RAP in a new domain, please include:

1. **Clear data source** - Provide link/citation to dataset
2. **Preprocessing steps** - Document any data cleaning
3. **Fitting results** - Report convergence statistics
4. **Comparison baseline** - Compare to domain-specific models
5. **Visualization** - Create plots showing convergence
6. **Statistical analysis** - Sample size, significance tests

### Validation Checklist
- [ ] Dataset description and source
- [ ] Data preprocessing code
- [ ] RAP model fitting code
- [ ] Baseline model comparison
- [ ] Convergence analysis (% at 85%)
- [ ] Statistical significance tests
- [ ] Visualization plots
- [ ] README documentation

## Questions?

- Open an issue for discussion
- Tag with `question` label
- Be respectful and constructive

## Attribution

Contributors will be acknowledged in:
- README acknowledgments section
- Git commit history
- Publications (for significant contributions)

## License

By contributing, you agree that your contributions will be licensed under the same MIT License that covers this project.

---

**Thank you for helping advance our understanding of recursive attractor dynamics!** 🥔
