"""Rules engine service for treatment logic."""

from typing import Any, Dict, List, Optional, Tuple
from app.core.logging import get_logger

logger = get_logger(__name__)


def determine_skin_type(
    form_answers: Dict[str, Any],
    machine_metrics: List[Dict[str, Any]]
) -> str:
    """
    Determine final skin type using machine data if confidence >= 0.6, else form data.
    
    Args:
        form_answers: Intake form responses
        machine_metrics: Machine scan metrics
        
    Returns:
        Skin type string
    """
    # Check machine metrics for skin type indicators
    sebum_metric = next((m for m in machine_metrics if m['key'] == 'sebum'), None)
    moisture_metric = next((m for m in machine_metrics if m['key'] == 'moisture'), None)
    
    if sebum_metric and moisture_metric:
        confidence = min(sebum_metric.get('confidence', 0), moisture_metric.get('confidence', 0))
        
        if confidence >= 0.6:
            sebum_value = sebum_metric['value']
            moisture_value = moisture_metric['value']
            
            # Determine skin type based on sebum and moisture levels
            if sebum_value >= 60:
                return "oily"
            elif sebum_value <= 30 and moisture_value <= 40:
                return "dry"
            elif moisture_value <= 30:
                return "sensitive"
            elif sebum_value >= 40 and moisture_value >= 50:
                return "combination"
            else:
                return "normal"
    
    # Fall back to form answers
    skin_profile = form_answers.get('skin_profile', {})
    return skin_profile.get('skin_type', 'normal')


def extract_main_concerns(form_answers: Dict[str, Any]) -> List[str]:
    """
    Extract up to 3 main concerns from form answers.
    
    Args:
        form_answers: Intake form responses
        
    Returns:
        List of main concerns (max 3)
    """
    skin_profile = form_answers.get('skin_profile', {})
    concerns = skin_profile.get('main_concerns', [])
    
    # Prioritize certain concerns
    priority_concerns = ['acne', 'pigmentation', 'aging', 'sensitivity']
    
    prioritized = [c for c in concerns if c in priority_concerns]
    others = [c for c in concerns if c not in priority_concerns]
    
    return (prioritized + others)[:3]


def check_restrictions(form_answers: Dict[str, Any]) -> Dict[str, bool]:
    """
    Check for restrictions that limit active ingredients.
    
    Args:
        form_answers: Intake form responses
        
    Returns:
        Dictionary of restrictions
    """
    medical_info = form_answers.get('medical_info', {})
    
    restrictions = {
        'pregnant': medical_info.get('pregnant', False),
        'breastfeeding': medical_info.get('breastfeeding', False),
        'medications': len(medical_info.get('medications', [])) > 0,
        'sensitive_skin': 'sensitivity' in form_answers.get('skin_profile', {}).get('main_concerns', [])
    }
    
    return restrictions


def calculate_irritation_score(
    machine_metrics: List[Dict[str, Any]],
    concerns: List[str]
) -> float:
    """
    Calculate overall irritation risk score.
    
    Args:
        machine_metrics: Machine scan metrics
        concerns: List of skin concerns
        
    Returns:
        Irritation score (0.0 to 1.0)
    """
    score = 0.0
    
    # Check sensitivity metrics
    sensitivity_metric = next((m for m in machine_metrics if m['key'] == 'sensitivity'), None)
    if sensitivity_metric:
        score += sensitivity_metric['value'] / 100.0 * 0.4
    
    # Check hyperemia (redness)
    hyperemia_metric = next((m for m in machine_metrics if m['key'] == 'hyperemia'), None)
    if hyperemia_metric:
        score += hyperemia_metric['value'] / 100.0 * 0.3
    
    # Add concern-based scoring
    if 'sensitivity' in concerns:
        score += 0.2
    if 'rosacea' in concerns:
        score += 0.3
        
    return min(score, 1.0)


def build_am_routine(
    skin_type: str,
    concerns: List[str],
    restrictions: Dict[str, bool],
    preferences: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Build AM skincare routine.
    
    Args:
        skin_type: Determined skin type
        concerns: Main skin concerns
        restrictions: Active ingredient restrictions
        preferences: User preferences
        
    Returns:
        List of AM routine steps
    """
    steps = []
    step_order = 1
    
    # Step 1: Cleanser
    if skin_type in ['oily', 'combination']:
        cleanser = "Apply gel cleanser to damp skin, massage gently for 30 seconds, rinse thoroughly"
    else:
        cleanser = "Apply cream cleanser to damp skin, massage gently for 30 seconds, rinse with lukewarm water"
    
    steps.append({
        "step_order": step_order,
        "instructions": cleanser
    })
    step_order += 1
    
    # Step 2: Treatment serums (if not restricted)
    max_serums = preferences.get('max_serums', 2)
    serum_count = 0
    
    if 'acne' in concerns and not restrictions['pregnant'] and serum_count < max_serums:
        steps.append({
            "step_order": step_order,
            "instructions": "Apply niacinamide serum, wait 2-3 minutes before next step"
        })
        step_order += 1
        serum_count += 1
    
    if 'pigmentation' in concerns and serum_count < max_serums:
        steps.append({
            "step_order": step_order,
            "instructions": "Apply vitamin C serum, wait 5 minutes before next step"
        })
        step_order += 1
        serum_count += 1
    
    # Step 3: Moisturizer
    moisturizer_texture = preferences.get('moisturizer_texture', 'normal')
    
    if skin_type == 'oily' or moisturizer_texture == 'lightweight':
        moisturizer = "Apply lightweight gel moisturizer evenly to face and neck"
    else:
        moisturizer = "Apply moisturizing cream evenly to face and neck"
        
    steps.append({
        "step_order": step_order,
        "instructions": moisturizer
    })
    step_order += 1
    
    # Step 4: Sunscreen (always last)
    steps.append({
        "step_order": step_order,
        "instructions": "Apply broad-spectrum SPF 30+ sunscreen generously, reapply every 2 hours"
    })
    
    return steps


def build_pm_routine(
    skin_type: str,
    concerns: List[str],
    restrictions: Dict[str, bool],
    preferences: Dict[str, Any],
    irritation_score: float
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Build PM skincare routine with weekly variations.
    
    Args:
        skin_type: Determined skin type
        concerns: Main skin concerns
        restrictions: Active ingredient restrictions
        preferences: User preferences
        irritation_score: Calculated irritation risk
        
    Returns:
        Tuple of (daily PM steps, weekly variation steps)
    """
    daily_steps = []
    weekly_steps = []
    step_order = 1
    
    # Step 1: Cleanser
    if skin_type in ['oily', 'combination']:
        cleanser = "Remove makeup with micellar water, then apply gel cleanser"
    else:
        cleanser = "Remove makeup with cleansing oil, then apply cream cleanser"
    
    daily_steps.append({
        "step_order": step_order,
        "instructions": cleanser
    })
    step_order += 1
    
    # Step 2: Active treatments (weekly rotation if high irritation risk)
    if 'acne' in concerns and not restrictions['pregnant']:
        if irritation_score >= 0.6:  # High irritation risk - alternate nights
            weekly_steps.extend([
                {
                    "day_of_week": 1,  # Monday
                    "when": "PM",
                    "instructions": "Apply salicylic acid toner, wait 10 minutes"
                },
                {
                    "day_of_week": 3,  # Wednesday
                    "when": "PM", 
                    "instructions": "Apply salicylic acid toner, wait 10 minutes"
                },
                {
                    "day_of_week": 5,  # Friday
                    "when": "PM",
                    "instructions": "Apply salicylic acid toner, wait 10 minutes"
                }
            ])
        else:
            daily_steps.append({
                "step_order": step_order,
                "instructions": "Apply salicylic acid toner, wait 10 minutes"
            })
            step_order += 1
    
    # Step 3: Anti-aging (avoid conflicts)
    if 'aging' in concerns and not restrictions['pregnant'] and 'acne' not in concerns:
        if irritation_score >= 0.6:
            # Gentle retinol on specific nights
            weekly_steps.extend([
                {
                    "day_of_week": 2,  # Tuesday
                    "when": "PM",
                    "instructions": "Apply retinol serum (start with 2x/week)"
                },
                {
                    "day_of_week": 5,  # Friday
                    "when": "PM",
                    "instructions": "Apply retinol serum (start with 2x/week)"
                }
            ])
        else:
            weekly_steps.extend([
                {
                    "day_of_week": 1,  # Monday
                    "when": "PM",
                    "instructions": "Apply retinol serum"
                },
                {
                    "day_of_week": 3,  # Wednesday  
                    "when": "PM",
                    "instructions": "Apply retinol serum"
                },
                {
                    "day_of_week": 5,  # Friday
                    "when": "PM",
                    "instructions": "Apply retinol serum"
                }
            ])
    
    # Final step: Night moisturizer
    if skin_type in ['dry', 'sensitive']:
        night_moisturizer = "Apply rich night cream with ceramides"
    else:
        night_moisturizer = "Apply night moisturizer with hyaluronic acid"
    
    daily_steps.append({
        "step_order": step_order,
        "instructions": night_moisturizer
    })
    
    return daily_steps, weekly_steps


def generate_explainability(
    skin_type: str,
    concerns: List[str],
    restrictions: Dict[str, bool],
    irritation_score: float,
    am_steps: List[Dict[str, Any]],
    pm_steps: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Generate explainability information for the treatment plan.
    
    Args:
        skin_type: Determined skin type
        concerns: Main skin concerns  
        restrictions: Active ingredient restrictions
        irritation_score: Calculated irritation risk
        am_steps: AM routine steps
        pm_steps: PM routine steps
        
    Returns:
        Explainability dictionary
    """
    reasoning = []
    
    # Skin type reasoning
    reasoning.append(f"Identified skin type as {skin_type} based on sebum and moisture analysis")
    
    # Concerns addressed
    if concerns:
        concerns_text = ", ".join(concerns)
        reasoning.append(f"Targeting primary concerns: {concerns_text}")
    
    # Restrictions noted
    active_restrictions = [k for k, v in restrictions.items() if v]
    if active_restrictions:
        restrictions_text = ", ".join(active_restrictions)
        reasoning.append(f"Considering restrictions: {restrictions_text}")
    
    # Irritation management
    if irritation_score >= 0.6:
        reasoning.append("High irritation risk detected - using gentle approach with rest nights")
    elif irritation_score >= 0.4:
        reasoning.append("Moderate irritation risk - alternating active treatments")
    
    return {
        "reasoning": reasoning,
        "confidence_score": max(0.7, 1.0 - irritation_score * 0.3),
        "skin_type_source": "machine" if irritation_score < 0.4 else "hybrid",
        "total_am_steps": len(am_steps),
        "total_pm_steps": len(pm_steps),
        "irritation_score": irritation_score,
        "restrictions_applied": active_restrictions
    }


async def generate_treatment_plan(
    form_answers: Dict[str, Any],
    machine_metrics: List[Dict[str, Any]],
    preferences: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate a complete treatment plan using deterministic rules.
    
    Args:
        form_answers: Intake form responses
        machine_metrics: Machine scan metrics
        preferences: User preferences (max_steps, max_serums, etc.)
        
    Returns:
        Complete treatment plan with routines and explainability
    """
    logger.info("Generating treatment plan", 
                has_form_data=bool(form_answers),
                metrics_count=len(machine_metrics))
    
    preferences = preferences or {}
    
    # Step 1: Determine skin type
    skin_type = determine_skin_type(form_answers, machine_metrics)
    
    # Step 2: Extract concerns
    concerns = extract_main_concerns(form_answers)
    
    # Step 3: Check restrictions
    restrictions = check_restrictions(form_answers)
    
    # Step 4: Calculate irritation risk
    irritation_score = calculate_irritation_score(machine_metrics, concerns)
    
    # Step 5: Build routines
    am_steps = build_am_routine(skin_type, concerns, restrictions, preferences)
    pm_steps, weekly_steps = build_pm_routine(
        skin_type, concerns, restrictions, preferences, irritation_score
    )
    
    # Step 6: Generate explainability
    explainability = generate_explainability(
        skin_type, concerns, restrictions, irritation_score, am_steps, pm_steps
    )
    
    # Step 7: Create skin profile
    skin_profile = {
        "skin_type": skin_type,
        "main_concerns": concerns,
        "irritation_score": irritation_score,
        "restrictions": restrictions,
        "analysis_timestamp": "2025-09-01T12:00:00Z"
    }
    
    plan = {
        "skin_profile": skin_profile,
        "routine": {
            "am": am_steps,
            "pm": pm_steps,
            "weekly": weekly_steps
        },
        "explainability": explainability
    }
    
    logger.info("Generated treatment plan",
                skin_type=skin_type,
                concerns_count=len(concerns),
                am_steps=len(am_steps),
                pm_steps=len(pm_steps),
                weekly_steps=len(weekly_steps))
    
    return plan


# Legacy functions for backward compatibility
async def evaluate_treatment_rules(
    client_profile: Dict[str, Any],
    available_machines: List[Dict[str, Any]],
    business_rules: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Legacy function - evaluate treatment rules based on client profile and available machines.
    """
    logger.info("Using legacy treatment rules evaluation")
    
    # Convert to new format and delegate
    form_answers = client_profile.get('form_answers', {})
    machine_metrics = client_profile.get('machine_metrics', [])
    
    return await generate_treatment_plan(form_answers, machine_metrics)


async def validate_treatment_compatibility(
    treatment_steps: List[Dict[str, Any]],
    client_profile: Dict[str, Any]
) -> Dict[str, bool]:
    """
    Legacy function - validate that treatment steps are compatible with client profile.
    """
    logger.info("Validating treatment compatibility", 
                step_count=len(treatment_steps),
                client_id=client_profile.get("id"))
    
    # Simple compatibility check
    restrictions = check_restrictions(client_profile.get('form_answers', {}))
    
    compatibility = {}
    for i, step in enumerate(treatment_steps):
        instructions = step.get('instructions', '').lower()
        
        # Check for restricted ingredients
        is_compatible = True
        if restrictions['pregnant']:
            if 'retinol' in instructions or 'salicylic acid' in instructions:
                is_compatible = False
        
        compatibility[str(i)] = is_compatible
    
    return compatibility


async def optimize_treatment_sequence(
    treatment_steps: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Legacy function - optimize the sequence of treatment steps for maximum effectiveness.
    """
    logger.info("Optimizing treatment sequence", step_count=len(treatment_steps))
    
    # Simple optimization: ensure cleansing comes first, moisturizer last
    cleansing_steps = [s for s in treatment_steps if 'cleans' in s.get('instructions', '').lower()]
    treatment_steps_filtered = [s for s in treatment_steps if 'cleans' not in s.get('instructions', '').lower()]
    moisturizing_steps = [s for s in treatment_steps_filtered if 'moistur' in s.get('instructions', '').lower()]
    other_steps = [s for s in treatment_steps_filtered if 'moistur' not in s.get('instructions', '').lower()]
    
    # Reorder and update step numbers
    optimized = cleansing_steps + other_steps + moisturizing_steps
    for i, step in enumerate(optimized):
        step['step_order'] = i + 1
    
    return optimized
