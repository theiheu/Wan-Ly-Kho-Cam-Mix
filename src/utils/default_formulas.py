"""
Predefined formulas for different types of feed and mix
"""

# Default feed formula for laying hens (2 tons per batch)
LAYER_FEED_FORMULA = {
    "Bắp": 1156,
    "Nành": 540,
    "Đá hạt": 108,
    "Đá bột mịn": 50,
    "Dầu": 4,
    "DCP": 29,
    "Cám gạo": 80,
}

# Default mix formula for laying hens (2 tons per batch)
LAYER_MIX_FORMULA = {
    "L-Lysine": 16,
    "DL-Methionine": 30,
    "Bio-Choline": 4,
    "Phytast": 3,
    "Performix 0.25% layer": 60,
    "Miamix": 60,
    "Premix 0.25% layer": 60,
    "Compound Enzyme FE808E": 3,
    "Carophy Red": 6,
    "P-Zym": 4,
    "Oxytetracylin": 0,
    "Tiamulin": 0,
    "Amox": 0,
    "Immunewall": 5,
    "Lysoforte Dry": 5,
    "Nutriprotect": 0,
    "Defitox L1": 16,
    "Men Ecobiol": 6,
    "Lactic LD": 20,
    "Sodium bicarbonate": 20,
    "Bột đá mịn": 45,
    "Muối": 74,
    "DCP": 0
}

# Example feed formula for broilers (2 tons per batch)
BROILER_FEED_FORMULA = {
    "Bắp": 1150,
    "Nành": 600,
    "Đá hạt": 100,
    "Đá bột mịn": 45,
    "Dầu": 10,
    "DCP": 35,
    "Cám gạo": 60,
}

# Example mix formula for broilers (2 tons per batch)
BROILER_MIX_FORMULA = {
    "L-Lysine": 20,
    "DL-Methionine": 35,
    "Bio-Choline": 5,
    "Phytast": 4,
    "Performix 0.25% broiler": 65,
    "Miamix": 65,
    "Premix 0.25% broiler": 65,
    "Compound Enzyme FE808E": 4,
    "Carophy Red": 0,
    "P-Zym": 5,
    "Oxytetracylin": 0,
    "Tiamulin": 0,
    "Amox": 0,
    "Immunewall": 8,
    "Lysoforte Dry": 6,
    "Nutriprotect": 0,
    "Defitox L1": 18,
    "Men Ecobiol": 8,
    "Lactic LD": 22,
    "Sodium bicarbonate": 18,
    "Bột đá mịn": 40,
    "Muối": 70,
    "DCP": 0
}

# Packaging information for inventory
PACKAGING_INFO = {
    "DCP": 25,  # 1 bag = 25kg
    "Đá hạt": 50,  # 1 bag = 50kg
    "Đá bột mịn": 50,  # 1 bag = 50kg
    "Cám gạo": 40,  # 1 bag = 40kg
    "L-Lysine": 25,
    "DL-Methionine": 25,
    "Bio-Choline": 25,
    "Phytast": 25,
    "Performix 0.25% layer": 25,
    "Performix 0.25% broiler": 25,
    "Miamix": 25,
    "Premix 0.25% layer": 25,
    "Premix 0.25% broiler": 25,
    "Compound Enzyme FE808E": 25,
    "Carophy Red": 25,
    "P-Zym": 25,
    "Immunewall": 25,
    "Lysoforte Dry": 25,
    "Defitox L1": 25,
    "Men Ecobiol": 25,
    "Lactic LD": 25,
    "Sodium bicarbonate": 25,
    "Bột đá mịn": 50,
    "Muối": 50
}

# Initial inventory data (example values)
INITIAL_INVENTORY = {
    # Feed ingredients
    "Bắp": 10000,
    "Nành": 5000,
    "Đá hạt": 1000,
    "Đá bột mịn": 500,
    "Dầu": 200,
    "DCP": 500,
    "Cám gạo": 800,

    # Mix ingredients
    "L-Lysine": 100,
    "DL-Methionine": 150,
    "Bio-Choline": 50,
    "Phytast": 50,
    "Performix 0.25% layer": 300,
    "Performix 0.25% broiler": 300,
    "Miamix": 300,
    "Premix 0.25% layer": 300,
    "Premix 0.25% broiler": 300,
    "Compound Enzyme FE808E": 50,
    "Carophy Red": 50,
    "P-Zym": 50,
    "Oxytetracylin": 0,
    "Tiamulin": 0,
    "Amox": 0,
    "Immunewall": 50,
    "Lysoforte Dry": 50,
    "Nutriprotect": 0,
    "Defitox L1": 100,
    "Men Ecobiol": 50,
    "Lactic LD": 100,
    "Sodium bicarbonate": 200,
    "Bột đá mịn": 500,
    "Muối": 500
}