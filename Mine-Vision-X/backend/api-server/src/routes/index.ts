import { Router, type IRouter } from "express";
import healthRouter from "./health";
import mineVisionRouter from "./mine-vision";

const router: IRouter = Router();

router.use(healthRouter);
router.use(mineVisionRouter);

export default router;
