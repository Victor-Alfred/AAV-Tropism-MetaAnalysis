"""
Quick normalization calculator for interactive use
Updated with specific measurement methods
"""
import numpy as np

def quick_normalize():
    """Interactive normalization calculator"""
    
    print("="*70)
    print("QUICK TROPISM NORMALIZATION CALCULATOR")
    print("="*70)
    
    print("\nSelect measurement method:")
    print("1. qPCR (vg/ug DNA)")
    print("2. Luciferase_ex_vivo (RLU or RLU/mg protein)")
    print("3. Luciferase_in_vivo (photons/sec/cm²/sr)")
    print("4. GFP/mCherry (%)")
    print("5. IHC (% or semi-quantitative)")
    print("6. Western (relative intensity)")
    print("7. ELISA (ng/mL or pg/mL)")
    print("8. Semi-quantitative (0-4 scale)")
    
    choice = input("\nEnter choice (1-8): ")
    raw_value = float(input("Enter raw value: "))
    
    if choice == '1':
        # qPCR
        log_value = np.log10(raw_value)
        normalized = (log_value - 6) / 4 * 5
        normalized = np.clip(normalized, 0, 5)
        
        print(f"\nqPCR Normalization:")
        print(f"  Raw value: {raw_value:.2e} vg/ug DNA")
        print(f"  Log10 value: {log_value:.2f}")
        print(f"  Normalized score: {normalized:.2f}")
        
    elif choice == '2':
        # Luciferase ex vivo
        log_value = np.log10(raw_value)
        normalized = (log_value - 3) / 5 * 5
        normalized = np.clip(normalized, 0, 5)
        
        print(f"\nLuciferase (ex vivo) Normalization:")
        print(f"  Raw value: {raw_value:.2e} RLU")
        print(f"  Log10 value: {log_value:.2f}")
        print(f"  Normalized score: {normalized:.2f}")
        
    elif choice == '3':
        # Luciferase in vivo (BLI)
        log_value = np.log10(raw_value)
        normalized = (log_value - 4) / 4 * 5
        normalized = np.clip(normalized, 0, 5)
        
        print(f"\nLuciferase (in vivo BLI) Normalization:")
        print(f"  Raw value: {raw_value:.2e} photons/sec/cm²/sr")
        print(f"  Log10 value: {log_value:.2f}")
        print(f"  Normalized score: {normalized:.2f}")
        
    elif choice == '4':
        # GFP/mCherry percentage
        normalized = (raw_value / 100) * 5
        normalized = np.clip(normalized, 0, 5)
        
        print(f"\nGFP/mCherry Normalization:")
        print(f"  Raw value: {raw_value:.1f}%")
        print(f"  Normalized score: {normalized:.2f}")
        
    elif choice == '5':
        # IHC
        if raw_value <= 5:
            # Semi-quantitative scale
            normalized = raw_value * 1.25
        elif raw_value <= 100:
            # Percentage
            normalized = (raw_value / 100) * 5
        else:
            # Absolute count
            log_value = np.log10(raw_value)
            normalized = (log_value - 3) / 5 * 5
        
        normalized = np.clip(normalized, 0, 5)
        
        print(f"\nIHC Normalization:")
        print(f"  Raw value: {raw_value}")
        print(f"  Normalized score: {normalized:.2f}")
        
    elif choice == '6':
        # Western blot
        if raw_value <= 1:
            normalized = raw_value * 5
        elif raw_value <= 100:
            normalized = (raw_value / 100) * 5
        else:
            log_value = np.log10(raw_value)
            normalized = (log_value - 3) / 5 * 5
        
        normalized = np.clip(normalized, 0, 5)
        
        print(f"\nWestern Blot Normalization:")
        print(f"  Raw value: {raw_value}")
        print(f"  Normalized score: {normalized:.2f}")
        
    elif choice == '7':
        # ELISA
        log_value = np.log10(raw_value)
        normalized = (log_value - 2) / 5 * 5
        normalized = np.clip(normalized, 0, 5)
        
        print(f"\nELISA Normalization:")
        print(f"  Raw value: {raw_value:.2e} ng/mL")
        print(f"  Log10 value: {log_value:.2f}")
        print(f"  Normalized score: {normalized:.2f}")
        
    elif choice == '8':
        # Semi-quantitative
        normalized = raw_value * 1.25
        normalized = np.clip(normalized, 0, 5)
        
        print(f"\nSemi-quantitative Normalization:")
        print(f"  Raw value: {raw_value:.1f} (0-4 scale)")
        print(f"  Normalized score: {normalized:.2f}")
    
    # Continue?
    again = input("\nNormalize another value? (y/n): ")
    if again.lower() == 'y':
        quick_normalize()

if __name__ == "__main__":
    quick_normalize()