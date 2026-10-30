
# AI Usage Log – COD Risk Prevention Assignment

**Prepared by:** Manju Bhargavi  
**Date:** 30 October 2026

## 1. Purpose of AI Assistance

AI assistance was used during project planning, Python development, debugging, documentation and business analysis.

The generated suggestions were reviewed and tested before being included in the project.

## 2. Areas Where AI Was Used

| Area | AI Assistance | Verification |
|---|---|---|
| Project planning | Helped divide the assignment into smaller development tasks. | Compared against assignment requirements. |
| Data cleaning | Helped develop Python preprocessing code. | Checked cleaning summaries and output columns. |
| Machine learning | Helped implement a Logistic Regression pipeline. | Evaluated using a chronological train-test split. |
| Decision engine | Helped structure risk-based business rules. | Tested sample orders against configured thresholds. |
| WhatsApp simulator | Helped design YES, NO, PREPAID and no-response scenarios. | Ran the terminal simulation with different responses. |
| Dashboard | Helped develop the Streamlit dashboard. | Ran the application locally and checked displayed metrics. |
| Documentation | Helped prepare the README and business memo. | Reviewed statements against project outputs and assumptions. |

## 3. AI Limitations and Corrections

### Issue 1: Accuracy does not tell the complete story

The model achieved 72.36% test accuracy, but RTO recall at the default 0.50 threshold was only 12.5%.

**Correction:** Reported ROC-AUC, average precision, precision, recall and confusion matrix instead of relying only on accuracy.

### Issue 2: Generated suggestions may not match actual code output

An explanation or suggested decision can differ from the behaviour of the currently saved Python file.

**Correction:** Used local execution and terminal output as the source of truth and checked the active configuration and source files.

### Issue 3: Financial estimates can be misunderstood

Estimated savings are not guaranteed business profits.

**Correction:** Clearly labelled financial calculations as illustrative estimates based on assignment assumptions.

### Issue 4: Customer privacy

Names, phone numbers and addresses must not be exposed unnecessarily.

**Correction:** Kept customer-level data private and used synthetic examples in the public decision log.

### Issue 5: False positives

A high-risk prediction does not prove that a customer will return an order.

**Correction:** Recommended manual review, first-time customer protection and disabling automatic cancellation.

## 4. Model Transparency

The predictive model is a scikit-learn Logistic Regression classifier.

It is not a generative AI model. It predicts an RTO probability from structured order information.

The WhatsApp workflow is a terminal-based simulation and is not connected to the live WhatsApp Business API.

## 5. Responsible AI Practices

- AI-generated code was tested before use.
- Business calculations were checked.
- Customer personal information was kept private.
- Model predictions are treated as decision-support signals.
- Human review is recommended for high-risk decisions.
- Automatic cancellation is disabled.

## 6. Known Limitations

- The model has modest predictive performance.
- RTO recall requires improvement through validation-based threshold tuning.
- The WhatsApp flow is a simulation.
- Dashboard financial figures are estimates.
- Historical patterns may not represent future orders.

## 7. Conclusion

AI assistance supported the development process, but the final implementation, testing, data handling and business recommendations require human verification.

**Prepared by:** Manju Bhargavi
