try:
    with fits.open(fits_file) as hdul:
        print(hdul.info())
        primary_hdu = hdul[0]
        compressed_image_hdu = hdul[1]
        table_hdu = hdul[2]

        header = copy.deepcopy(primary_hdu.header)
        data_array = copy.deepcopy(compressed_image_hdu.data)
        table_data = copy.deepcopy(table_hdu.data)
except FileNotFoundError:
    print(f"Fits file ''{fits_file}'' not found")
except Exception as e:
    print(f"Error {e}")

for card in header.cards:
    print(f"{card.keyword}  {card.value} // {card.comment}")

column_names = table_data.columns.names
print(column_names)
frequencies = table_data['freq']

num_samples = header['NSAMPLES']
ref_time = header['REF_TIME']