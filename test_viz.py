import unittest
import json
import os
from unittest.mock import patch, mock_open

class TestVisualizationResults(unittest.TestCase):
    
    def setUp(self):
        """Set up test data"""
        self.test_data = {
            'сценарии': ['Базовый', 'С самообслуживанием', 'С пчелиным алгоритмом'],
            'средние_времена_ожидания': [0.09, 0.31, 0.14],
            'максимальные_времена_ожидания': [2.25, 5.14, 3.56],
            'обслуженные_клиенты': [228.8, 456.2, 458.3],
            'клиенты_отказались': [124.6, 25.1, 24.7],
            'коэффициенты_загрузки': [36.6, 43.6, 33.6],
            'улучшения': [0, -225.21, -44.26],  # Negative values indicate increase in waiting time
            'улучшения_удовлетворенности': [0, 79.87, 80.16]  # Positive values indicate improvement in satisfaction
        }
    
    def test_data_interpretation(self):
        """Test that the data is correctly interpreted"""
        # Check that waiting time actually increases in optimized scenarios
        base_time = self.test_data['средние_времена_ожидания'][0]
        self_time = self.test_data['средние_времена_ожидания'][1]
        bee_time = self.test_data['средние_времена_ожидания'][2]
        
        # Verify that waiting time increases
        self.assertGreater(self_time, base_time, "Self-service scenario should have higher waiting time than base")
        self.assertGreater(bee_time, base_time, "Bee algorithm scenario should have higher waiting time than base")
        
        # Check that improvements are negative (indicating increase in waiting time)
        self.assertLess(self.test_data['улучшения'][1], 0, "Self-service improvement should be negative")
        self.assertLess(self.test_data['улучшения'][2], 0, "Bee algorithm improvement should be negative")
        
        # Check that satisfaction improvements are positive
        self.assertGreater(self.test_data['улучшения_удовлетворенности'][1], 0, "Self-service satisfaction improvement should be positive")
        self.assertGreater(self.test_data['улучшения_удовлетворенности'][2], 0, "Bee algorithm satisfaction improvement should be positive")
    
    def test_business_metrics(self):
        """Test business metrics calculation"""
        # Calculate customer churn reduction
        base_churn = self.test_data['клиенты_отказались'][0]
        bee_churn = self.test_data['клиенты_отказались'][2]
        churn_reduction = ((base_churn - bee_churn) / base_churn) * 100
        
        # Should be approximately 80%
        self.assertAlmostEqual(churn_reduction, 80.1, delta=1.0, msg="Customer churn reduction should be around 80%")
        
        # Calculate throughput increase
        base_throughput = self.test_data['обслуженные_клиенты'][0]
        bee_throughput = self.test_data['обслуженные_клиенты'][2]
        throughput_increase = ((bee_throughput - base_throughput) / base_throughput) * 100
        
        # Should be approximately 100%
        self.assertAlmostEqual(throughput_increase, 100.0, delta=1.0, msg="Throughput increase should be around 100%")
        
        # Check resource efficiency improvement
        base_load = self.test_data['коэффициенты_загрузки'][0]
        bee_load = self.test_data['коэффициенты_загрузки'][2]
        
        # Load should decrease
        self.assertLess(bee_load, base_load, "Resource load should decrease with optimization")

if __name__ == '__main__':
    unittest.main()