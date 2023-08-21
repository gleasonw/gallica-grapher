import React from "react";
import * as DropdownMenu from "@radix-ui/react-dropdown-menu";
import { ArrowDownIcon } from "@radix-ui/react-icons";

export function GallicaDropdown<T extends string | number>({
  itemsToDisplay,
  onChange,
  selected,
}: {
  itemsToDisplay: T[];
  onChange: (value: T) => void;
  selected: T | string;
}) {
  return (
    <DropdownMenu.Root>
      <DropdownMenu.Trigger asChild>
        <button
          className={
            "flex items-center gap-10 hover:bg-gray-200 rounded shadow-sm p-3 border-2 cursor-pointer"
          }
        >
          {selected}
          <ArrowDownIcon />
        </button>
      </DropdownMenu.Trigger>

      <DropdownMenu.Portal className={"w-full"}>
        <DropdownMenu.Content className="border rounded-lg shadow-lg w-full bg-white">
          {itemsToDisplay.map((item) => (
            <DropdownMenu.Item
              key={item}
              onSelect={() => onChange(item)}
              className="p-3 hover:bg-gray-200 w-full text-left cursor-pointer"
            >
              {item}
            </DropdownMenu.Item>
          ))}
        </DropdownMenu.Content>
      </DropdownMenu.Portal>
    </DropdownMenu.Root>
  );
}
