"""
Unit tests for MetricsService
"""

import pytest
from app.services.metrics_service import MetricsService


class TestMetricsService:
    """Test suite for MetricsService"""
    
    def test_calculate_cost(self):
        """Test AWS Bedrock cost calculation"""
        service = MetricsService()
        
        # Test with known values
        input_tokens = 1000
        output_tokens = 500
        
        cost = service.calculate_cost(input_tokens, output_tokens)
        
        # Expected: (1000 * 0.00025/1000) + (500 * 0.00125/1000)
        # = 0.00025 + 0.000625 = 0.000875
        assert cost == pytest.approx(0.000875, abs=0.000001)
    
    def test_calculate_cost_zero_tokens(self):
        """Test cost calculation with zero tokens"""
        service = MetricsService()
        cost = service.calculate_cost(0, 0)
        assert cost == 0.0
    
    def test_calculate_cost_large_numbers(self):
        """Test cost calculation with large token counts"""
        service = MetricsService()
        
        # 1M input tokens, 500K output tokens
        input_tokens = 1_000_000
        output_tokens = 500_000
        
        cost = service.calculate_cost(input_tokens, output_tokens)
        
        # Expected: (1M * 0.00025/1000) + (500K * 0.00125/1000)
        # = 0.25 + 0.625 = 0.875
        assert cost == pytest.approx(0.875, abs=0.001)
    
    def test_calculate_field_completeness_empty(self):
        """Test completeness calculation with empty data"""
        service = MetricsService()
        completeness, count = service.calculate_field_completeness({})
        
        assert completeness == 0.0
        assert count == 0
    
    def test_calculate_field_completeness_full(self):
        """Test completeness calculation with all fields"""
        service = MetricsService()
        
        medical_data = {
            "patient_name": "John Doe",
            "date_of_birth": "1980-01-01",
            "diagnoses": ["Hypertension", "Type 2 Diabetes"],
            "medications": ["Metformin 500mg"],
            "lab_values": {"glucose": "120 mg/dL"},
            "procedures": ["Annual physical"],
            "allergies": ["Penicillin"],
            "vital_signs": {"bp": "120/80"},
            "notes": "Patient doing well"
        }
        
        completeness, count = service.calculate_field_completeness(medical_data)
        
        assert completeness == 100.0
        assert count == 9
    
    def test_calculate_field_completeness_partial(self):
        """Test completeness calculation with partial data"""
        service = MetricsService()
        
        medical_data = {
            "patient_name": "John Doe",
            "date_of_birth": "1980-01-01",
            "diagnoses": ["Hypertension"],
            "medications": [],  # Empty list shouldn't count
            "lab_values": {},   # Empty dict shouldn't count
        }
        
        completeness, count = service.calculate_field_completeness(medical_data)
        
        # Only 3 fields populated: patient_name, date_of_birth, diagnoses
        # 3 / 9 = 33.33%
        assert completeness == pytest.approx(33.33, abs=0.1)
        assert count == 3
    
    def test_calculate_field_completeness_null_values(self):
        """Test that None/null values don't count"""
        service = MetricsService()
        
        medical_data = {
            "patient_name": None,
            "date_of_birth": "",
            "diagnoses": None,
            "medications": [],
        }
        
        completeness, count = service.calculate_field_completeness(medical_data)
        
        assert completeness == 0.0
        assert count == 0


class TestMetricsServiceIntegration:
    """Integration tests requiring DynamoDB (mocked)"""
    
    @pytest.mark.skip(reason="Requires DynamoDB mock setup")
    def test_get_prompt_metrics(self):
        """Test retrieving metrics for a prompt version"""
        # Would test with mocked DynamoDB
        pass
    
    @pytest.mark.skip(reason="Requires DynamoDB mock setup")
    def test_compare_prompts(self):
        """Test statistical comparison of prompts"""
        # Would test with mocked DynamoDB
        pass
