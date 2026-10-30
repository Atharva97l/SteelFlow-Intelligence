from pathlib import Path


def main() -> None:
    data_dir = Path(__file__).parent / "data"
    tables = sorted(data_dir.glob("*.parquet"))
    print(f"SteelFlow data directory: {data_dir}")
    print(f"Parquet tables discovered: {len(tables)}")
    print("Run `python scripts/profile_data.py` to generate the EDA catalog.")


if __name__ == "__main__":
    main()
