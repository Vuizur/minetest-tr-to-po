import polib
import os

EMPTY_LINE = "<EMPTY LINE>\n"  # polib doesn't recognize empty comments as comments, so if we want to maintain the free lines
# between the entries in the original tr file, we have to add a comment that is not empty


def tr_to_po(tr_filename: str, po_filename: str) -> None:
    with open(tr_filename, "r", encoding="utf-8") as f:
        lines = f.readlines()

    po = polib.POFile(wrapwidth=0) # wrapwidth=0 means no line wrapping, otherwise we will get some bugs
    po.metadata = {
        "Content-Type": "text/plain; charset=utf-8",
    }
    comment = ""
    for line in lines:
        if line.startswith("#"):
            comment += line
            continue
        if "=" not in line:
            if line.strip() != "":
                print("Invalid line:", line)
                continue
            else:
                comment += EMPTY_LINE
        if "=" in line:
            key, value = line.split("=", 1)
            po.append(
                polib.POEntry(msgid=key, msgstr=value.rstrip("\n"), tcomment=comment)
            )
            comment = ""

    # Write the po file
    po.save(po_filename)


def po_to_tr(po_filename: str, tr_filename: str) -> None:
    po = polib.pofile(po_filename)
    with open(tr_filename, "w", encoding="utf-8") as f:
        tr_entries: list[str] = []

        for entry in po:
            s = ""
            if entry.tcomment:
                s += entry.tcomment.replace(EMPTY_LINE, "\n")
            s += entry.msgid + "=" + entry.msgstr
            tr_entries.append(s)
        f.write("\n".join(tr_entries))


def convert_tr_to_po_and_back_and_check_diff(tr_filename: str) -> None:
    po_filename = tr_filename.replace(".tr", ".po")
    tr_filename_new = tr_filename.replace(".tr", "_new.tr")

    tr_to_po(tr_filename, po_filename)
    po_to_tr(po_filename, tr_filename_new)

    with open(tr_filename, "r", encoding="utf-8") as f:
        lines = f.readlines()
    with open(tr_filename_new, "r", encoding="utf-8") as f:
        lines_new = f.readlines()

    already_failed = False
    # Iterate over both files and compare them line by line
    for old_line, new_line in zip(lines, lines_new):
        # If this is the last line, remove the newline character

        if old_line.rstrip("\n") != new_line.rstrip(
            "\n"
        ):  # Currently there are some translation files that have an extra newline at the end
            if not already_failed:
                print("Difference found in file:", tr_filename)
                already_failed = True
            # Not sure what the standard should be
            print("Difference found:")
            print("Old line:", old_line)
            print(len(old_line))
            print("New line:", new_line)
            print(len(new_line))
            print()
            # raise Exception("Difference found in file:", tr_filename)


def check_if_conversion_is_lossless_for_all_files(mineclone_dir: str) -> None:
    # Recursively iterate over all files in the directory
    for root, _, files in os.walk(mineclone_dir):
        for file in files:
            if file.endswith(".tr") and not file.endswith("_new.tr"):
                convert_tr_to_po_and_back_and_check_diff(os.path.join(root, file))


def purge_all_temp_files(mineclone_dir: str):
    # Recursively iterate over all files in the directory
    for root, _, files in os.walk(mineclone_dir):
        for file in files:
            if file.endswith("_new.tr"):
                os.remove(os.path.join(root, file))
            if file.endswith(".po"):
                os.remove(os.path.join(root, file))


if __name__ == "__main__":
    # convert_tr_to_po_and_back_and_check_diff("mcl_doc_basics.de.tr")
    # convert_tr_to_po_and_back_and_check_diff("mcl_blast_furnace.dk.tr")
    # convert_tr_to_po_and_back_and_check_diff("hudbars.pt.tr")
    #check_if_conversion_is_lossless_for_all_files(
    #    r"C:\Users\hanne\Downloads\minetest-5.7.0-win64\games\MineClone2"
    #)
    # purge_all_temp_files(r"C:\Users\hanne\Downloads\minetest-5.7.0-win64\games\MineClone2")
