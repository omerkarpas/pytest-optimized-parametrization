# conftest.py

import pytest
import logging

log = logging.getLogger(__name__)

def pytest_generate_tests(metafunc):
    test_name = metafunc.function.__name__
    log.trace("Generating tests for %s with %s fixtures", test_name, number_of_fixtures_per_test)
    
    command_markers = metafunc.config.getoption("-m")
    test_markers = [marker.name for marker in metafunc.definition.iter_markers()]
    add_synthetic_markers_to_markers_list(metafunc, test_markers, test_name)
    
    is_markers_in_test = not command_markers or not should_skip_based_on_expression(test_markers, command_markers)
    command_keywords = metafunc.config.getoption("-k")
    is_keywords_in_test = not command_keywords or not should_skip_based_on_expression([test_name], command_keywords)
    
    # Test is eligible for parametrization if it contains the required markers OR keywords
    test_eligible_for_parametrization = is_markers_in_test and is_keywords_in_test
    
    if test_eligible_for_parametrization:
        # PARAMETRIZE TESTS HERE
        pass
    else:
        log.trace(
            "Not parametrizing test %s as it does not contain the required %s, markers=%s, keywords=%s",
            test_name,
            "markers" if not is_markers_in_test else "keywords",
            test_markers,
            command_keywords,
        )

def should_skip_based_on_expression(test_markers_or_keywords: list, command_expression: str) -> bool:
    if not command_expression:
        return False

    def evaluate_expression(expression: str, markers_or_keywords: list) -> bool:
        expression = expression.strip()
        if 'or' in expression:
            return any(evaluate_expression(part, markers_or_keywords) for part in expression.split(' or '))
        if 'and' in expression:
            return all(evaluate_expression(part, markers_or_keywords) for part in expression.split(' and '))
        if expression.startswith('not '):
            marker = expression[4:].strip()
            return marker not in markers_or_keywords
        return expression in markers_or_keywords
    
    return not evaluate_expression(command_expression, test_markers_or_keywords)

def skip_item_based_on_marker(item, config) -> bool:
    marker_expression = config.getoption("markexpr").strip()
    if not marker_expression:
        return False

    or_parts = marker_expression.split(' or ')
    for part in or_parts:
        and_parts = part.split(' and ')
        if all(check_marker_presence(item, sub_part.strip()) for sub_part in and_parts):
            return False

    log.trace("skipping item %s based on item marker", item)
    return True

def check_marker_presence(item, marker) -> bool:
    negation = 'not ' in marker
    actual_marker = marker.replace('not ', '').strip()
    has_marker = item.get_closest_marker(actual_marker) is not None
    return not has_marker if negation else has_marker
