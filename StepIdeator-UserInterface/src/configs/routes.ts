import {MagicIcon} from "../../public/icons";

export const RoutesConfig = [
    {
        path: '/page',
        name: 'Step by step',
        icon: MagicIcon
    },
]

export const getPageName = (pathname: string) => {
    const ret = RoutesConfig.find(route => route.path === pathname)
    if(ret === undefined) return RoutesConfig[0].name
    return ret.name
}