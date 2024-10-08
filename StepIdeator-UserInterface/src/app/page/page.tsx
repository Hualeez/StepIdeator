"use client";

import {PaintProvider} from "@/app/page/provider";
import Page from "@/app/page/Main";

export default function PaintPageWrapper() {

    return (
        <PaintProvider>
            <Page />
        </PaintProvider>
    );
};

