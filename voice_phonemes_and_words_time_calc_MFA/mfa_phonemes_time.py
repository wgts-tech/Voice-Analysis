import os
import csv
from textgrid import TextGrid
import textgrid


input_dir = "noisy_and_clean_voice"  
output_dir = "phonemes_time_csv"    

os.makedirs(output_dir, exist_ok=True)


def convert_textgrid_with_tiers_to_csv():    
    textgrid_files = [f for f in os.listdir(input_dir) if f.endswith(".TextGrid")]

    if not textgrid_files:
        print("No TextGrid files found in the input directory.")
        return

    for tg_file in textgrid_files:
        tg_path = os.path.join(input_dir, tg_file)
        output_file_path = os.path.join(output_dir, tg_file.replace(".TextGrid", ".csv"))
        
        try:
            tg = TextGrid.fromFile(tg_path)
            
            with open(output_file_path, "w", newline="", encoding="utf-8") as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow(["Phoneme", "Start_Time(sec)", "End_Time(sec)", "Duration(sec)"])                  
                
                for tier in tg.tiers:
                    if tier.name in ["phones"]:  
                        for interval in tier.intervals:                                            
                            text = interval.mark.strip() if interval.mark else ""
                            start_time = interval.minTime
                            end_time = interval.maxTime
                            duration = end_time - start_time
                            
                            if text:
                                csv_writer.writerow([text, f"{start_time:.3f}", f"{end_time:.3f}", f"{duration:.3f}"])

            print(f"Converted: {tg_file} -> {output_file_path}")

        except Exception as e:
            print(f"Error processing {tg_file}: {e}")

convert_textgrid_with_tiers_to_csv()
