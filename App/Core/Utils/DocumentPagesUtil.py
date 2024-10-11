from typing import List


class DocumentPagesUtil:
    @staticmethod
    def __cups_pack_block(block: List[int]) -> str:
        if len(block) < 2:
            return str(block[-1])

        if len(block) == 2:
            return f"{str(block[0])},{str(block[1])}"

        return f"{str(block[0])}-{str(block[-1])}"

    @staticmethod
    def cups_pack(numbers: List[int]) -> str:
        numbers = sorted(numbers)

        packed = []
        block = []

        for number in numbers:
            len_block = len(block)

            if not len_block:
                block.append(number)
                continue

            if (block[-1] + 1) != number:
                packed.append(DocumentPagesUtil.__cups_pack_block(block))

                block = []

            block.append(number)

        if len(block):
            packed.append(DocumentPagesUtil.__cups_pack_block(block))

        return ",".join(packed)

    @staticmethod
    def cups_unpack(string: str, max_page: int = 0) -> List[int]:
        numbers = string.split(",")
        ints = []

        for number in numbers:
            if '-' not in number:
                ints.append(int(number))
                continue

            segments = number.split('-')
            ints += [*range(int(segments[0]), int(segments[1]) + 1)]

        ints = sorted(ints)

        if max_page > 0:
            ints = list(filter(lambda x: x <= max_page, ints))

        return ints
