import os
import csv

def main():
    
    no_of_uis = int(input('Enter no. of UIs tested (should have folders named from 1 to this number): '))
    output_file = 'raw_dataset.csv'

    for temp_i in range(no_of_uis):
        i = temp_i+1

        directory_path = f'{i}/csv'

        files = os.listdir(directory_path)

        csv_files = [file for file in files if file.endswith('.csv')]
        csv_count = 0
        updated_rows = []

        for csv_file in csv_files:
            file_path = os.path.join(directory_path, csv_file)
            
            with open(file_path, 'r', newline='') as csvfile:
                reader = csv.reader(csvfile)
                j = 0
                for row in reader:
                    if j==0:
                        if csv_count == 0:
                            updated_rows.append(row)
                    else:
                        row_int = [float(value) for value in row]
                        if csv_count == 0:
                            updated_rows.append(row_int)
                        else:
                            updated_rows[j][-1] += row_int[-1]
                    j += 1
            
            csv_count += 1
        
        # print(updated_rows)

        for j in range(len(updated_rows)):
            if j > 0:
                updated_rows[j][-1] /= csv_count

        with open(output_file, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for j in range(len(updated_rows)):
                if j == 0:
                    if i == 1:
                        writer.writerow(updated_rows[j])
                else:
                    writer.writerow(updated_rows[j])        


# Run the main function
if __name__ == "__main__":
    main()
