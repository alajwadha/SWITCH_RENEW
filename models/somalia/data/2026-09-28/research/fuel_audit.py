"""Audit the public World Bank Somalia RTEP archive without changing raw data.

Uses only Python's standard library. Run with --help for the file arguments.
The optional annotated CSV preserves all source columns and labels source-price
availability separately from the modeled close estimate. It does not convert
currencies, average markets, or turn retail prices into generator fuel costs.
"""

import argparse
import csv
from datetime import date
from decimal import Decimal, InvalidOperation
import hashlib
import io
import json
from pathlib import Path
import re
import zipfile


def read_csv_zip(path):
    with zipfile.ZipFile(path) as archive:
        names = [name for name in archive.namelist() if name.lower().endswith('.csv')]
        if len(names) != 1:
            raise ValueError(f'Expected one CSV inside {path}; found {names}')
        content = archive.read(names[0])
    reader = csv.DictReader(io.StringIO(content.decode('utf-8-sig')))
    return names[0], reader.fieldnames, list(reader), content


def audit(archive_path, metadata_path=None):
    name, fields, rows, csv_bytes = read_csv_zip(archive_path)
    required = {'ISO3', 'mkt_name', 'geo_id', 'price_date', 'currency',
                'spatially_interpolated', 'fuel_diesel', 'o_fuel_diesel',
                'h_fuel_diesel', 'l_fuel_diesel', 'c_fuel_diesel'}
    if not required.issubset(fields):
        raise ValueError(f'Missing columns: {sorted(required - set(fields))}')
    errors = []
    keys = set()
    series = {}
    for line, row in enumerate(rows, start=2):
        key = (row['geo_id'], row['price_date'])
        if key in keys:
            errors.append(f'Duplicate location/month at CSV line {line}')
        keys.add(key)
        series.setdefault(row['geo_id'], []).append(row)
        try:
            d = date.fromisoformat(row['price_date'])
            if d.day != 1 or d.year != int(row['year']) or d.month != int(row['month']):
                errors.append(f'Inconsistent month/year at CSV line {line}')
        except ValueError:
            errors.append(f'Invalid date at CSV line {line}')
        if row['ISO3'] != 'SOM':
            errors.append(f'Non-Somalia row at CSV line {line}')
        if row['spatially_interpolated'] not in {'0', '1'}:
            errors.append(f'Invalid spatial interpolation flag at CSV line {line}')
        for field in ['fuel_diesel', 'o_fuel_diesel', 'h_fuel_diesel',
                      'l_fuel_diesel', 'c_fuel_diesel']:
            if row[field]:
                try:
                    if not Decimal(row[field]).is_finite() or Decimal(row[field]) <= 0:
                        errors.append(f'Non-positive/non-finite {field} at CSV line {line}')
                except InvalidOperation:
                    errors.append(f'Non-numeric {field} at CSV line {line}')
        if all(row[f] for f in ['l_fuel_diesel', 'h_fuel_diesel', 'c_fuel_diesel']):
            low, high, close = (Decimal(row[f]) for f in
                                ['l_fuel_diesel', 'h_fuel_diesel', 'c_fuel_diesel'])
            if not low <= close <= high:
                errors.append(f'Modeled close outside low/high at CSV line {line}')
    aggregate_ids = {row['geo_id'] for row in rows
                     if row['mkt_name'] == 'Market Average'}
    market_rows = [row for row in rows if row['geo_id'] not in aggregate_ids]
    dates = sorted({row['price_date'] for row in rows})
    observed_field_rows = [row for row in rows if row['fuel_diesel']]
    summary = {
        'dataset_id': 'SOM_2023_RTEP_v01_M',
        'source_catalogue': 'https://microdata.worldbank.org/catalog/6130',
        'csv_member': name,
        'archive_sha256': hashlib.sha256(Path(archive_path).read_bytes()).hexdigest(),
        'csv_sha256': hashlib.sha256(csv_bytes).hexdigest(),
        'rows': len(rows), 'columns': len(fields), 'months': len(dates),
        'start_month': dates[0], 'end_month': dates[-1],
        'locations_including_publisher_aggregate': len(series),
        'physical_market_locations': len(series) - len(aggregate_ids),
        'publisher_aggregate_locations': sorted(aggregate_ids),
        'market_rows_excluding_aggregate': len(market_rows),
        'unique_location_month_keys': len(keys),
        'complete_rectangular_panel': len(rows) == len(dates) * len(series),
        'currency_labels': sorted({row['currency'] for row in rows}),
        'source_price_field_nonblank': len(observed_field_rows),
        'source_price_field_nonblank_excluding_aggregate': sum(
            bool(row['fuel_diesel']) for row in market_rows),
        'source_price_field_latest_month': max(
            (row['price_date'] for row in observed_field_rows), default=None),
        'modeled_close_nonblank': sum(bool(row['c_fuel_diesel']) for row in rows),
        'unit': 'not validated without matching metadata archive',
        'validation_errors': errors,
        'interpretation': [
            'fuel_diesel is the publisher source-price field; its presence is not independent verification of a new survey quote.',
            'o/h/l/c_fuel_diesel are modeled open/high/low/close estimates, not raw observations or statistical confidence intervals.',
            'spatially_interpolated=0 does not imply absence of temporal imputation.',
            'No national average, USD conversion, wholesale adjustment, or SWITCH fuel-cost conversion is calculated.'
        ]
    }
    if metadata_path:
        meta_name, _, meta_rows, _ = read_csv_zip(metadata_path)
        meta = next(row for row in meta_rows if row['iso3'] == 'SOM')
        if 'Fuel (Diesel) (1 L,' not in meta['components']:
            raise ValueError('Expected diesel one-litre unit absent from metadata')
        if {row['currency'] for row in rows} != {meta['currency']}:
            raise ValueError('Metadata and data currency labels disagree')
        summary['unit'] = f"{meta['currency']}/L (publisher labels; no currency conversion)"
        summary['metadata_member'] = meta_name
        summary['metadata_archive_sha256'] = hashlib.sha256(
            Path(metadata_path).read_bytes()).hexdigest()
        summary['metadata_number_of_markets_modeled'] = int(meta['number_of_markets_modeled'])
        summary['metadata_source_observation_end'] = meta['end_date_observations']
        match = re.search(r'fuel_diesel:\s*(\d+)', meta['number_of_observations_other'])
        summary['metadata_reported_diesel_observations'] = int(match.group(1)) if match else None
        summary['metadata_observation_count_matches_nonblank_source_fields'] = (
            summary['metadata_reported_diesel_observations'] == len(observed_field_rows))
    return summary, fields, rows, aggregate_ids


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('--metadata-archive', type=Path)
    parser.add_argument('--json-out', type=Path)
    parser.add_argument('--annotated-out', type=Path)
    args = parser.parse_args()
    input_paths = {p.resolve() for p in [args.archive, args.metadata_archive] if p}
    output_paths = [p.resolve() for p in [args.json_out, args.annotated_out] if p]
    if input_paths.intersection(output_paths):
        raise ValueError('Audit outputs must not overwrite either raw archive')
    if len(output_paths) != len(set(output_paths)):
        raise ValueError('JSON and annotated CSV need different output paths')
    summary, fields, rows, aggregates = audit(args.archive, args.metadata_archive)
    if args.annotated_out:
        args.annotated_out.parent.mkdir(parents=True, exist_ok=True)
        added = ['record_role', 'source_price_status', 'modeled_close_status', 'unit_verified']
        with args.annotated_out.open('w', newline='', encoding='utf-8') as stream:
            writer = csv.DictWriter(stream, fieldnames=fields + added)
            writer.writeheader()
            for row in rows:
                writer.writerow(dict(row,
                    record_role=('publisher_aggregate' if row['geo_id'] in aggregates else 'market'),
                    source_price_status=('source_price_field_present' if row['fuel_diesel'] else 'source_price_field_missing'),
                    modeled_close_status=('modeled_estimate' if row['c_fuel_diesel'] else 'missing'),
                    unit_verified=summary['unit']))
    result = json.dumps(summary, indent=2, ensure_ascii=False) + '\n'
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(result, encoding='utf-8')
    print(result)
    raise SystemExit(bool(summary['validation_errors']))


if __name__ == '__main__':
    main()
