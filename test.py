# A tiny story to show how Python makes decisions and does calculations.

print("----------\nKidaz nhar Meryem\n----------")

her_mood = input("kteb l mood (fr7ana, ka3ya, m3sba): ").lower()
weather = input("Kteb ta9s (mochmis, rainy): ").lower()
hours_sleep = int(input("Ch7al mn sa3a dn3as: "))

# Start with base points
surprise_points = 0

# Condition 1: Mood
if her_mood == "fr7ana":
    surprise_points += 5
    print("Mood: Meryem frana! +5 points")
else:
    surprise_points += 2
    print("Mood: Jaha kti2ab. +2 points")

# Condition 2: Weather
if weather == "mochmis":
    surprise_points += 3
    print("Ta9s: Mochmis! +3 points")
else:
    surprise_points += 1
    print("Ta9s: Mghyem. +1 point")

# Condition 3: Sleep amount (calculation)
if hours_sleep >= 7:
    surprise_points += 4
    print(f"N3as: N3sat {hours_sleep}h, mzyan! +4 points")
else:
    surprise_points += 1
    print(f"N3as: Ghir {hours_sleep}h…. +1 point")

# Final result
print("\Mjmo3 no9at:", surprise_points)

# Interpretation
if surprise_points >= 12:
    print("Lyouma daz mzyan!")
else:
    print("Nhar mabihch!")
