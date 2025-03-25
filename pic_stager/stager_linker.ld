ENTRY(alignstack)
SECTIONS
{
	.text :
	{
        *(.text.alignstack)
		*(.text.stager_main)
	}
}

