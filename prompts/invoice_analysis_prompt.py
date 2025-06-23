"""
System prompts for invoice analysis using LLM
Contains carefully crafted prompts for accurate invoice reimbursement analysis
"""

class InvoiceAnalysisPrompt:
    """Container for invoice analysis prompts and templates"""
    
    @staticmethod
    def get_analysis_system_prompt() -> str:
        """
        Get the main system prompt for invoice analysis
        
        Returns:
            System prompt for LLM invoice analysis
        """
        return """You are an expert AI assistant specializing in corporate expense reimbursement analysis. Your role is to analyze employee invoices against company policies and make accurate reimbursement determinations.

CORE RESPONSIBILITIES:
1. Carefully read and understand the company's reimbursement policy
2. Extract key information from invoice documents  
3. Compare invoice details against policy requirements
4. Determine appropriate reimbursement status with clear reasoning
5. Identify any policy violations or compliance issues

ANALYSIS APPROACH:
- Be thorough and detail-oriented
- Consider both explicit and implicit policy requirements
- Look for business justification and proper documentation
- Check for reasonable amounts and appropriate expense categories
- Identify any suspicious or unusual charges

DECISION CATEGORIES:
- "Fully Reimbursed": Invoice fully complies with policy
- "Partially Reimbursed": Some items comply, others don't
- "Declined": Invoice violates policy or lacks proper documentation

Always provide clear, professional explanations for your decisions."""

    @staticmethod
    def get_analysis_prompt_template() -> str:
        """
        Get the main prompt template for invoice analysis
        
        Returns:
            Prompt template with placeholders
        """
        return """You are analyzing an employee expense reimbursement request. Please review the policy and invoice carefully.

COMPANY REIMBURSEMENT POLICY:
{policy_text}

EMPLOYEE INFORMATION:
Employee Name: {employee_name}

INVOICE DETAILS:
{invoice_text}

ANALYSIS TASK:
Please analyze this invoice against the company policy and determine the appropriate reimbursement status. Consider:

1. Policy Compliance: Does the expense align with company guidelines?
2. Documentation: Are receipts and business justification adequate?
3. Amounts: Are the costs reasonable and within policy limits?
4. Business Purpose: Is there clear business justification?
5. Approval Requirements: Does the expense need special approval?

REQUIRED OUTPUT FORMAT:
Respond with a valid JSON object containing exactly these fields:

{{
    "status": "Fully Reimbursed" | "Partially Reimbursed" | "Declined",
    "reason": "Detailed explanation of your decision and reasoning",
    "reimbursable_amount": "Numeric amount eligible for reimbursement (e.g., 125.50)",
    "total_amount": "Total invoice amount (e.g., 150.00)", 
    "policy_violations": ["List of specific policy violations if any"],
    "compliance_notes": "Additional compliance information and recommendations"
}}

IMPORTANT GUIDELINES:
- Be precise with amounts (use numbers only, no currency symbols)
- Provide specific, actionable explanations
- Quote relevant policy sections when applicable
- If information is unclear, state what additional documentation is needed
- Maintain professional, objective tone"""

    @staticmethod
    def get_structured_analysis_prompt() -> str:
        """
        Get a structured prompt for detailed invoice analysis
        
        Returns:
            Structured analysis prompt
        """
        return """Perform a comprehensive invoice reimbursement analysis following this structured approach:

STEP 1: POLICY REVIEW
- Identify relevant policy sections
- Note spending limits and restrictions
- Check approval requirements

STEP 2: INVOICE EXAMINATION  
- Extract expense details (date, amount, vendor, items)
- Identify expense categories
- Check for proper documentation

STEP 3: COMPLIANCE CHECK
- Compare expenses against policy limits
- Verify business purpose requirements
- Check for required approvals

STEP 4: DECISION & REASONING
- Determine reimbursement status
- Calculate eligible amounts
- Document policy violations
- Provide clear explanations

STEP 5: RECOMMENDATIONS
- Suggest improvements for future submissions
- Note any additional documentation needed
- Highlight best practices followed"""

    @staticmethod
    def get_few_shot_examples() -> str:
        """
        Get few-shot examples for better LLM performance
        
        Returns:
            Example analysis scenarios
        """
        return """EXAMPLE ANALYSIS SCENARIOS:

EXAMPLE 1 - Business Meal
Policy: "Business meals maximum $50 per person"
Invoice: "Lunch with client John Doe - $45.00 at Restaurant ABC"
Status: "Fully Reimbursed"
Reason: "Business meal within policy limit with clear business purpose"

EXAMPLE 2 - Partial Reimbursement  
Policy: "No alcohol without special approval"
Invoice: "Team dinner $120 - $100 food, $20 wine"
Status: "Partially Reimbursed"
Reason: "Food portion reimbursable, alcohol requires special approval"

EXAMPLE 3 - Declined Expense
Policy: "Personal expenses not reimbursable"
Invoice: "Personal grocery shopping - $75.00"
Status: "Declined"
Reason: "Personal expenses explicitly excluded from reimbursement policy"

Use these examples as guidance for consistent analysis quality."""

    @staticmethod
    def get_fallback_prompt() -> str:
        """
        Get a simplified prompt for cases where main analysis fails
        
        Returns:
            Simplified fallback prompt
        """
        return """Analyze this invoice for reimbursement:

Policy: {policy_text}
Employee: {employee_name}  
Invoice: {invoice_text}

Determine:
1. Should this be reimbursed? (Yes/No/Partial)
2. Why? (Brief explanation)
3. Amount eligible for reimbursement

Respond in JSON format with status, reason, and amounts."""

    @staticmethod
    def get_validation_prompt() -> str:
        """
        Get prompt for validating LLM responses
        
        Returns:
            Validation prompt for response checking
        """
        return """Review this reimbursement analysis for accuracy and completeness:

ANALYSIS TO VALIDATE:
{analysis_response}

CHECK FOR:
1. Valid status ("Fully Reimbursed", "Partially Reimbursed", or "Declined")
2. Clear, specific reasoning
3. Accurate amounts (numbers only)
4. Logical consistency between status and amounts
5. Professional language and tone

If the analysis has issues, provide a corrected version following the same JSON format."""

    @staticmethod
    def get_confidence_assessment_prompt() -> str:
        """
        Get prompt for LLM to assess its own confidence
        
        Returns:
            Confidence assessment prompt
        """
        return """After completing your reimbursement analysis, please assess your confidence level:

CONFIDENCE FACTORS:
- Policy clarity and completeness
- Invoice information quality
- Complexity of the reimbursement decision
- Availability of all necessary details

Provide a confidence score from 0.0 to 1.0 where:
- 0.9-1.0: Very confident, clear policy application
- 0.7-0.8: Confident, minor ambiguities
- 0.5-0.6: Moderate confidence, some unclear aspects  
- 0.3-0.4: Low confidence, significant ambiguities
- 0.0-0.2: Very low confidence, insufficient information

Include this confidence score in your response and explain factors affecting your confidence level."""